"""Доменный хендлер: приём фото, удаление фона, постобработка.

Принимает:
  - F.photo (обычное фото в Telegram, может быть пережато)
  - F.document с mime_type image/jpeg|png|webp (файл — сохраняет качество)

Возвращает результат как **document** (PNG, чтобы прозрачность сохранилась —
photo Telegram пережимает в JPEG и теряет альфа-канал).

Под результатом — inline-кнопки для смены фона / размера.
Cutout RGBA-PNG кладётся в LRU-кэш по короткому request_id; кнопки
ссылаются на него через callback_data, чтобы не светить большие байты.
"""
from __future__ import annotations

import io
import logging

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    BufferedInputFile,
    CallbackQuery,
    InputMediaDocument,
    Message,
)

from bot.config import settings
from bot.database import async_session
from bot.database.crud import (
    get_or_create_user,
    get_user_default_model,
    get_user_language,
    increment_user_download_count,
    save_remover_request,
    update_user_model,
)
from bot.emojis import E
from bot.i18n import t
from bot.keyboards.inline import (
    get_back_keyboard,
    get_bg_color_keyboard,
    get_result_keyboard,
    get_settings_keyboard,
    get_size_keyboard,
)
from bot.services import cache as cutout_cache
from bot.services.remover import (
    SUPPORTED_MODELS,
    FileTooLargeError,
    InvalidImageError,
    ProcessingError,
    ResolutionTooLargeError,
    apply_background,
    classify_error,
    compose_result,
    remove_background,
    resize_result,
)

logger = logging.getLogger(__name__)
router = Router()


# === FSM для замены фона на свою картинку ===

class BgImageStates(StatesGroup):
    waiting_bg_image = State()


# === Утилиты ===

ALLOWED_MIME = ("image/jpeg", "image/jpg", "image/png", "image/webp")


def _error_text(exc: Exception, lang: str) -> str:
    """Перевод исключения в i18n-текст для юзера"""
    code = classify_error(exc)
    if code == "file_too_large":
        return t("error.too_large", lang, max_mb=settings.max_input_mb)
    if code == "resolution_too_large":
        return t(
            "error.resolution_too_large",
            lang,
            max_res=settings.max_resolution,
        )
    if code == "invalid_image":
        return t("error.not_image", lang)
    if code == "timeout":
        return t("error.timeout", lang)
    return t("error.processing_failed", lang)


async def _download_input(bot: Bot, message: Message) -> bytes | None:
    """Скачивает фото или документ-изображение в bytes. Возвращает None если не подходит."""
    file_id: str | None = None
    if message.photo:
        # photo — массив миниатюр, берём максимальную
        file_id = message.photo[-1].file_id
    elif message.document:
        mime = (message.document.mime_type or "").lower()
        if mime not in ALLOWED_MIME:
            return None
        # доп. ограничение по размеру до скачивания
        if message.document.file_size and message.document.file_size > settings.max_input_mb * 1024 * 1024:
            raise FileTooLargeError("document too large")
        file_id = message.document.file_id

    if not file_id:
        return None

    buf = io.BytesIO()
    await bot.download(file_id, destination=buf)
    buf.seek(0)
    return buf.read()


# === Команда /settings ===

@router.message(Command("settings"))
async def cmd_settings(message: Message) -> None:
    """Команда /settings — выбор модели rembg"""
    async with async_session() as session:
        await get_or_create_user(
            session=session,
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            full_name=message.from_user.full_name,
        )
        lang = await get_user_language(session, message.from_user.id)
        model = await get_user_default_model(session, message.from_user.id)

    await message.answer(
        t("remover.settings", lang, model=model),
        reply_markup=get_settings_keyboard(lang, current_model=model),
    )


@router.callback_query(F.data == "process_photo")
async def process_photo_prompt(callback: CallbackQuery) -> None:
    """Просим прислать фото в чат"""
    async with async_session() as session:
        lang = await get_user_language(session, callback.from_user.id)
    await callback.message.answer(t("remover.send_prompt", lang))
    await callback.answer()


@router.callback_query(F.data == "open_settings")
async def open_settings_cb(callback: CallbackQuery) -> None:
    """Открыть настройки через inline-кнопку"""
    async with async_session() as session:
        lang = await get_user_language(session, callback.from_user.id)
        model = await get_user_default_model(session, callback.from_user.id)

    await callback.message.edit_text(
        t("remover.settings", lang, model=model),
        reply_markup=get_settings_keyboard(lang, current_model=model),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("set_model_"))
async def set_model(callback: CallbackQuery) -> None:
    """Сохранение выбранной модели"""
    model = callback.data.replace("set_model_", "")
    if model not in SUPPORTED_MODELS:
        await callback.answer(f"{E['cross']} unknown model")
        return

    async with async_session() as session:
        await update_user_model(session, callback.from_user.id, model)
        lang = await get_user_language(session, callback.from_user.id)

    await callback.message.edit_text(
        t("remover.settings", lang, model=model),
        reply_markup=get_settings_keyboard(lang, current_model=model),
    )
    await callback.answer(t("remover.model_set", lang, model=model))


# === Приём фото и обработка ===

@router.message(
    F.photo
    | (F.document & F.document.mime_type.in_({"image/jpeg", "image/jpg", "image/png", "image/webp"}))
)
async def handle_photo(message: Message, state: FSMContext, bot: Bot) -> None:
    """Главный хендлер — приём фото и удаление фона"""
    # Если ждём фото-фон для постобработки — обработаем отдельно
    current_state = await state.get_state()
    if current_state == BgImageStates.waiting_bg_image.state:
        await _handle_bg_image(message, state, bot)
        return

    async with async_session() as session:
        await get_or_create_user(
            session=session,
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            full_name=message.from_user.full_name,
        )
        lang = await get_user_language(session, message.from_user.id)
        model = await get_user_default_model(session, message.from_user.id)

    # Скачиваем
    try:
        input_bytes = await _download_input(bot, message)
    except FileTooLargeError as e:
        await message.answer(_error_text(e, lang))
        return
    except Exception as e:
        logger.exception("Ошибка скачивания: %s", e)
        await message.answer(t("error.generic", lang))
        return

    if not input_bytes:
        await message.answer(t("error.not_image", lang))
        return

    # Сообщение "обрабатываю"
    progress = await message.answer(t("remover.processing", lang))

    # Запускаем rembg
    try:
        cutout_png, elapsed_ms, resolution = await remove_background(
            input_bytes=input_bytes,
            model_name=model,
            bg_color=None,
        )
    except (FileTooLargeError, ResolutionTooLargeError, InvalidImageError, ProcessingError) as e:
        await progress.delete()
        await message.answer(_error_text(e, lang))
        return
    except Exception as e:
        logger.exception("Ошибка обработки: %s", e)
        await progress.delete()
        await message.answer(t("error.processing_failed", lang))
        return

    # Сохраняем cutout в кэш — для кнопок постобработки
    request_id = cutout_cache.put(cutout_png, model_used=model)

    # Считаем размеры для БД
    input_kb = len(input_bytes) // 1024
    output_kb = len(cutout_png) // 1024

    # Удаляем "обрабатываю" и шлём результат
    try:
        await progress.delete()
    except Exception:
        pass

    caption = t(
        "remover.done",
        lang,
        model=model,
        resolution=resolution,
        ms=elapsed_ms,
    )
    await message.answer_document(
        document=BufferedInputFile(cutout_png, filename="no_bg.png"),
        caption=caption,
        reply_markup=get_result_keyboard(request_id, lang),
    )

    # БД: счётчик и запись
    try:
        async with async_session() as session:
            await increment_user_download_count(session, message.from_user.id)
            await save_remover_request(
                session=session,
                user_id=message.from_user.id,
                model_used=model,
                input_size_kb=input_kb,
                output_size_kb=output_kb,
                input_resolution=resolution,
                processing_time_ms=elapsed_ms,
                bg_color=None,
            )
    except Exception as e:
        logger.warning("Не удалось сохранить статистику: %s", e)

    # input_bytes уйдёт в GC — на диск ничего не клали (всё в памяти).


# === Возврат в главное меню из result-keyboard ===

@router.callback_query(F.data == "result_to_menu")
async def result_to_menu(callback: CallbackQuery, state: FSMContext) -> None:
    """Юзер нажал 'В главное меню' под результатом-документом.
    Отправляем новое сообщение с меню (текущее — document, edit_text не сработает)."""
    from bot.keyboards.inline import get_start_keyboard

    await state.clear()
    async with async_session() as session:
        lang = await get_user_language(session, callback.from_user.id)

    await callback.message.answer(
        t("start.welcome", lang, name=callback.from_user.first_name),
        reply_markup=get_start_keyboard(user_id=callback.from_user.id, lang=lang),
    )
    # клавиатуру под результатом убираем — чтобы юзер не пытался её жать ещё раз
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass
    await callback.answer()


# === Постобработка: меню фона ===

async def _safe_edit_caption(callback: CallbackQuery, **kwargs) -> None:
    """edit_caption с глотанием 'message is not modified'"""
    from aiogram.exceptions import TelegramBadRequest
    try:
        await callback.message.edit_caption(**kwargs)
    except TelegramBadRequest as e:
        if "not modified" not in str(e):
            raise


async def _strip_keyboard(message: Message) -> None:
    """Убирает inline-клавиатуру у сообщения (без шума при ошибках)"""
    try:
        await message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass


@router.callback_query(F.data.startswith("bg_menu:"))
async def bg_menu(callback: CallbackQuery) -> None:
    """Открывает выбор фона. Формат: bg_menu:{rid}:{current_size}"""
    parts = callback.data.split(":", 2)
    if len(parts) != 3:
        await callback.answer("bad data")
        return
    _, request_id, current_size = parts

    if cutout_cache.get(request_id) is None:
        async with async_session() as session:
            lang = await get_user_language(session, callback.from_user.id)
        await callback.answer(t("remover.expired", lang), show_alert=True)
        return

    async with async_session() as session:
        lang = await get_user_language(session, callback.from_user.id)

    await _safe_edit_caption(
        callback,
        caption=t("remover.bg_menu", lang),
        reply_markup=get_bg_color_keyboard(request_id, lang, current_size=current_size),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("size_menu:"))
async def size_menu(callback: CallbackQuery) -> None:
    """Открывает выбор размера. Формат: size_menu:{rid}:{current_bg}"""
    parts = callback.data.split(":", 2)
    if len(parts) != 3:
        await callback.answer("bad data")
        return
    _, request_id, current_bg = parts

    if cutout_cache.get(request_id) is None:
        async with async_session() as session:
            lang = await get_user_language(session, callback.from_user.id)
        await callback.answer(t("remover.expired", lang), show_alert=True)
        return

    async with async_session() as session:
        lang = await get_user_language(session, callback.from_user.id)

    await _safe_edit_caption(
        callback,
        caption=t("remover.size_menu", lang),
        reply_markup=get_size_keyboard(request_id, lang, current_bg=current_bg),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("back_result:"))
async def back_result(callback: CallbackQuery) -> None:
    """Возврат к меню результата. Формат: back_result:{rid}:{cur_bg}:{cur_size}"""
    parts = callback.data.split(":", 3)
    if len(parts) != 4:
        await callback.answer("bad data")
        return
    _, request_id, current_bg, current_size = parts

    cached = cutout_cache.get(request_id)
    if cached is None:
        async with async_session() as session:
            lang = await get_user_language(session, callback.from_user.id)
        await callback.answer(t("remover.expired", lang), show_alert=True)
        return

    _, model = cached
    async with async_session() as session:
        lang = await get_user_language(session, callback.from_user.id)

    await _safe_edit_caption(
        callback,
        caption=t("remover.result_simple", lang, model=model),
        reply_markup=get_result_keyboard(request_id, lang, current_bg=current_bg, current_size=current_size),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("bg_apply:"))
async def bg_apply(callback: CallbackQuery) -> None:
    """Применить фон. Формат: bg_apply:{rid}:{color}:{current_size}"""
    parts = callback.data.split(":", 3)
    if len(parts) != 4:
        await callback.answer("bad data")
        return
    _, request_id, color, current_size = parts

    async with async_session() as session:
        lang = await get_user_language(session, callback.from_user.id)

    cached = cutout_cache.get(request_id)
    if cached is None:
        await callback.answer(t("remover.expired", lang), show_alert=True)
        return
    cutout_png, model = cached

    await callback.answer()

    try:
        out_png = await compose_result(cutout_png, bg_color=color, size_mode=current_size)
    except Exception as e:
        logger.exception("compose_result (bg) failed: %s", e)
        await callback.message.answer(t("error.processing_failed", lang))
        return

    filename = f"no_bg_{color}_{current_size}.png" if color != "transparent" else f"no_bg_{current_size}.png"
    await _strip_keyboard(callback.message)
    await callback.message.answer_document(
        document=BufferedInputFile(out_png, filename=filename),
        caption=t("remover.caption_variant", lang, variant=color),
        reply_markup=get_result_keyboard(request_id, lang, current_bg=color, current_size=current_size),
    )

    try:
        async with async_session() as session:
            await save_remover_request(
                session=session,
                user_id=callback.from_user.id,
                model_used=model,
                input_size_kb=len(cutout_png) // 1024,
                output_size_kb=len(out_png) // 1024,
                input_resolution="—",
                processing_time_ms=0,
                bg_color=color,
            )
    except Exception as e:
        logger.warning("save_remover_request bg variant: %s", e)


@router.callback_query(F.data.startswith("size_apply:"))
async def size_apply(callback: CallbackQuery) -> None:
    """Применить размер. Формат: size_apply:{rid}:{mode}:{current_bg}"""
    parts = callback.data.split(":", 3)
    if len(parts) != 4:
        await callback.answer("bad data")
        return
    _, request_id, mode, current_bg = parts

    async with async_session() as session:
        lang = await get_user_language(session, callback.from_user.id)

    cached = cutout_cache.get(request_id)
    if cached is None:
        await callback.answer(t("remover.expired", lang), show_alert=True)
        return
    cutout_png, model = cached

    await callback.answer()

    try:
        out_png = await compose_result(cutout_png, bg_color=current_bg, size_mode=mode)
    except Exception as e:
        logger.exception("compose_result (size) failed: %s", e)
        await callback.message.answer(t("error.processing_failed", lang))
        return

    await _strip_keyboard(callback.message)
    await callback.message.answer_document(
        document=BufferedInputFile(out_png, filename=f"no_bg_{current_bg}_{mode}.png"),
        caption=t("remover.caption_variant", lang, variant=mode),
        reply_markup=get_result_keyboard(request_id, lang, current_bg=current_bg, current_size=mode),
    )


# === Постобработка: своя картинка как фон ===

@router.callback_query(F.data.startswith("bg_image:"))
async def bg_image_prompt(callback: CallbackQuery, state: FSMContext) -> None:
    """Юзер выбрал 'Своя картинка' — ждём от него фото-фон. Формат: bg_image:{rid}:{current_size}"""
    parts = callback.data.split(":", 2)
    if len(parts) != 3:
        await callback.answer("bad data")
        return
    _, request_id, current_size = parts

    cached = cutout_cache.get(request_id)
    async with async_session() as session:
        lang = await get_user_language(session, callback.from_user.id)
    if cached is None:
        await callback.answer(t("remover.expired", lang), show_alert=True)
        return

    await state.set_state(BgImageStates.waiting_bg_image)
    await state.update_data(request_id=request_id, current_size=current_size)

    await callback.message.answer(
        t("remover.bg_image_prompt", lang),
        reply_markup=get_back_keyboard(lang),
    )
    await callback.answer()


async def _handle_bg_image(message: Message, state: FSMContext, bot: Bot) -> None:
    """Юзер прислал фон-картинку для замены"""
    data = await state.get_data()
    request_id = data.get("request_id")
    current_size = data.get("current_size", "original")

    async with async_session() as session:
        lang = await get_user_language(session, message.from_user.id)

    cached = cutout_cache.get(request_id) if request_id else None
    if cached is None:
        await state.clear()
        await message.answer(t("remover.expired", lang))
        return
    cutout_png, model = cached

    try:
        bg_bytes = await _download_input(bot, message)
    except FileTooLargeError as e:
        await message.answer(_error_text(e, lang))
        return
    if not bg_bytes:
        await message.answer(t("error.not_image", lang))
        return

    progress = await message.answer(t("remover.processing", lang))

    try:
        out_png = await compose_result(cutout_png, bg_image_bytes=bg_bytes, size_mode=current_size)
    except Exception as e:
        logger.exception("compose_result (bg_image) failed: %s", e)
        try:
            await progress.delete()
        except Exception:
            pass
        await message.answer(t("error.processing_failed", lang))
        return

    try:
        await progress.delete()
    except Exception:
        pass

    # Кэш НЕ перезаписываем — оригинальный cutout остаётся для повторных операций
    await message.answer_document(
        document=BufferedInputFile(out_png, filename="no_bg_custom.png"),
        caption=t("remover.caption_variant", lang, variant="custom"),
        reply_markup=get_result_keyboard(request_id, lang, current_bg="transparent", current_size=current_size),
    )

    await state.clear()
    # bg_bytes — в памяти, освободится GC
