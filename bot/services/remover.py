"""Сервис удаления фона через rembg

- Поддержка моделей: u2net / isnet-general-use
- Кэш rembg-сессий (new_session() дорогая операция) с LRU-ограничением
- Глобальный семафор Semaphore(2) — rembg тяжёлый на CPU
- Блокирующие вызовы оборачиваются в asyncio.to_thread()
- Валидация размера и разрешения, ресайз больших изображений
- Постобработка: замена фона на цвет / картинку / квадратный канвас
"""
from __future__ import annotations

import asyncio
import io
import logging
import threading
import time
from collections import OrderedDict
from typing import Any

from PIL import Image

from bot.config import settings

logger = logging.getLogger(__name__)


# === Константы ===

# Список поддерживаемых моделей
SUPPORTED_MODELS = ("u2net", "isnet-general-use")

# Защита от decompression bomb (Pillow по умолчанию рубит на 90млн пикселей)
Image.MAX_IMAGE_PIXELS = 50_000_000

# Жёсткий лимит площади (для ранней проверки в validate_input)
MAX_PIXELS = 50_000_000

# Глобальный семафор — не более 2 одновременных обработок (rembg грузит CPU)
_semaphore = asyncio.Semaphore(2)

# Кэш rembg-сессий: model_name -> Session (LRU, max 2 одновременно)
_sessions: "OrderedDict[str, Any]" = OrderedDict()
_MAX_SESSIONS = 2
# Защита от гонки при первой инициализации сессии (синхронный лок,
# т.к. _get_session вызывается из asyncio.to_thread)
_sessions_lock = threading.Lock()


# === Исключения ===

class FileTooLargeError(Exception):
    """Файл превышает допустимый размер"""


class ResolutionTooLargeError(Exception):
    """Разрешение изображения превышает допустимое"""


class InvalidImageError(Exception):
    """Битый или неподдерживаемый файл"""


class ProcessingError(Exception):
    """Ошибка работы rembg"""


# === Внутренние утилиты ===

def _get_session(model_name: str):
    """Возвращает rembg-сессию для модели (с LRU-кэшем).

    Потокобезопасно — защищено threading.Lock, т.к. функция вызывается
    как из asyncio.to_thread (rembg-обработка), так и при прогреве.
    """
    from rembg import new_session  # импорт ленивый — пакет тяжёлый

    if model_name not in SUPPORTED_MODELS:
        model_name = "u2net"

    with _sessions_lock:
        sess = _sessions.get(model_name)
        if sess is not None:
            _sessions.move_to_end(model_name)
            return sess

        logger.info("Инициализация rembg-сессии для модели %s", model_name)
        sess = new_session(model_name)
        _sessions[model_name] = sess
        _sessions.move_to_end(model_name)
        # эвикт самой старой если превысили лимит
        while len(_sessions) > _MAX_SESSIONS:
            old_name, _ = _sessions.popitem(last=False)
            logger.info("Эвикт rembg-сессии %s (LRU)", old_name)
        return sess


def _resize_if_needed(img: Image.Image, max_side: int) -> Image.Image:
    """Если картинка больше max_side по любой стороне — ресайзим с сохранением пропорций"""
    w, h = img.size
    if max(w, h) <= max_side:
        return img
    ratio = max_side / max(w, h)
    new_size = (int(w * ratio), int(h * ratio))
    logger.info("Ресайз изображения %sx%s → %sx%s", w, h, *new_size)
    return img.resize(new_size, Image.Resampling.LANCZOS)


def _hex_to_rgb(color: str) -> tuple[int, int, int]:
    """Превращает '#RRGGBB' или 'white' в (R, G, B)"""
    named = {
        "white": (255, 255, 255),
        "black": (0, 0, 0),
        "green": (0, 177, 64),  # классический chroma key
        "red": (255, 0, 0),
        "blue": (0, 0, 255),
    }
    if color in named:
        return named[color]
    if color.startswith("#") and len(color) == 7:
        return (int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16))
    return (255, 255, 255)


def _apply_solid_bg(rgba: Image.Image, color: str) -> Image.Image:
    """Накладывает RGBA на сплошной цветной фон"""
    bg = Image.new("RGB", rgba.size, _hex_to_rgb(color))
    bg.paste(rgba, mask=rgba.split()[3])
    return bg


def _apply_image_bg(rgba: Image.Image, bg_bytes: bytes) -> Image.Image:
    """Накладывает RGBA-объект на картинку-фон.

    Логика: фон — это холст (его размеры сохраняются). Cutout вписывается
    в центр холста по принципу "contain" с сохранением пропорций.
    """
    bg = Image.open(io.BytesIO(bg_bytes)).convert("RGB")
    bw, bh = bg.size

    # подгоняем cutout, чтобы он вписался в фон (contain)
    fitted = rgba.copy()
    fitted.thumbnail((bw, bh), Image.Resampling.LANCZOS)

    x = (bw - fitted.width) // 2
    y = (bh - fitted.height) // 2
    bg.paste(fitted, (x, y), mask=fitted.split()[3])
    return bg


def _resize_to_box(rgba: Image.Image, target: int) -> Image.Image:
    """Ресайзит RGBA, сохраняя пропорции, чтобы влезло в target x target"""
    img = rgba.copy()
    img.thumbnail((target, target), Image.Resampling.LANCZOS)
    return img


def _square_pad(rgba: Image.Image, target: int) -> Image.Image:
    """Делает квадратный канвас target x target с прозрачным паддингом"""
    img = _resize_to_box(rgba, target)
    canvas = Image.new("RGBA", (target, target), (0, 0, 0, 0))
    x = (target - img.width) // 2
    y = (target - img.height) // 2
    canvas.paste(img, (x, y), img)
    return canvas


# === Публичные функции ===

def validate_input(input_bytes: bytes) -> tuple[int, int]:
    """Валидирует размер и разрешение. Возвращает (width, height).
    Бросает FileTooLargeError / InvalidImageError / ResolutionTooLargeError.
    Ресайз НЕ делает — это решает remove_background.
    """
    size_mb = len(input_bytes) / (1024 * 1024)
    if size_mb > settings.max_input_mb:
        raise FileTooLargeError(
            f"Файл {size_mb:.1f} МБ > лимита {settings.max_input_mb} МБ"
        )
    try:
        # читаем только заголовок — не декодируем полное изображение
        img = Image.open(io.BytesIO(input_bytes))
        w, h = img.size
    except Exception as e:
        raise InvalidImageError(f"Не удалось распознать изображение: {e}") from e

    # проверка площади (decompression bomb)
    if w * h > MAX_PIXELS:
        raise ResolutionTooLargeError(
            f"Изображение {w}x{h} ({w*h} px) превышает лимит {MAX_PIXELS} px"
        )
    # проверка по стороне (защита от очень узких/длинных картинок)
    if max(w, h) > settings.max_resolution * 4:
        raise ResolutionTooLargeError(
            f"Сторона {max(w, h)} превышает лимит {settings.max_resolution * 4}"
        )

    # окончательная валидация целостности
    try:
        Image.open(io.BytesIO(input_bytes)).verify()
    except Exception as e:
        raise InvalidImageError(f"Битый файл: {e}") from e

    return (w, h)


def _do_remove_bg(input_bytes: bytes, model_name: str) -> tuple[bytes, str]:
    """Синхронная функция: выполняет rembg.remove(). Возвращает (rgba_png_bytes, "WxH").
    Запускается в to_thread(). Здесь же делаем ресайз больших картинок.
    """
    from rembg import remove

    img = Image.open(io.BytesIO(input_bytes))
    img = _resize_if_needed(img, settings.max_resolution)
    img = img.convert("RGBA")
    resolution = f"{img.width}x{img.height}"

    sess = _get_session(model_name)
    try:
        # rembg.remove() умеет принимать PIL.Image и возвращать PIL.Image
        out_img = remove(img, session=sess)
    except Exception as e:
        raise ProcessingError(f"rembg.remove(): {e}") from e

    buf = io.BytesIO()
    out_img.save(buf, format="PNG")
    return buf.getvalue(), resolution


async def remove_background(
    input_bytes: bytes,
    model_name: str = "u2net",
    bg_color: str | None = None,
) -> tuple[bytes, int, str]:
    """Удаляет фон с изображения.

    Args:
        input_bytes: байты входного изображения (jpg/png/webp).
        model_name: одна из SUPPORTED_MODELS.
        bg_color: None (прозрачный) | "white" | "black" | "green" | "#RRGGBB".

    Returns:
        (output_png_bytes, processing_time_ms, "WxH").

    Raises:
        FileTooLargeError, ResolutionTooLargeError, InvalidImageError, ProcessingError.
    """
    # Валидация размера и формата (быстро, синхронно)
    validate_input(input_bytes)

    if model_name not in SUPPORTED_MODELS:
        model_name = "u2net"

    started = time.perf_counter()

    async with _semaphore:
        try:
            rgba_png, resolution = await asyncio.to_thread(
                _do_remove_bg, input_bytes, model_name
            )
        except (FileTooLargeError, InvalidImageError, ProcessingError):
            raise
        except Exception as e:
            raise ProcessingError(str(e)) from e

    # Постобработка фона (если задан bg_color и это не "transparent")
    if bg_color and bg_color != "transparent":
        rgba = Image.open(io.BytesIO(rgba_png)).convert("RGBA")
        composed = _apply_solid_bg(rgba, bg_color)
        out = io.BytesIO()
        composed.save(out, format="PNG")
        rgba_png = out.getvalue()

    elapsed_ms = int((time.perf_counter() - started) * 1000)
    logger.info(
        "remove_background: model=%s res=%s bg=%s time=%dms in=%dKB out=%dKB",
        model_name,
        resolution,
        bg_color,
        elapsed_ms,
        len(input_bytes) // 1024,
        len(rgba_png) // 1024,
    )
    return rgba_png, elapsed_ms, resolution


async def apply_background(
    cutout_png: bytes,
    bg_color: str | None = None,
    bg_image_bytes: bytes | None = None,
) -> bytes:
    """Постобработка готового cutout (RGBA PNG): замена фона.

    bg_color = None → возвращает как есть (прозрачный).
    bg_color = "white"/"black"/"green"/"#RRGGBB" → сплошной фон.
    bg_image_bytes != None → накладывает на картинку-фон.
    """
    def _do() -> bytes:
        rgba = Image.open(io.BytesIO(cutout_png)).convert("RGBA")
        if bg_image_bytes:
            out = _apply_image_bg(rgba, bg_image_bytes)
        elif bg_color and bg_color != "transparent":
            out = _apply_solid_bg(rgba, bg_color)
        else:
            return cutout_png
        buf = io.BytesIO()
        out.save(buf, format="PNG")
        return buf.getvalue()

    return await asyncio.to_thread(_do)


async def resize_result(
    cutout_png: bytes,
    mode: str,
) -> bytes:
    """Изменение размера готового cutout.

    mode:
      "original" — без изменений
      "512"      — fit в 512x512 (с сохранением пропорций, без паддинга)
      "1024"     — fit в 1024x1024
      "square_pad_512"  — квадрат 512x512 с прозрачным паддингом
      "square_pad_1024" — квадрат 1024x1024 с прозрачным паддингом
    """
    if mode == "original":
        return cutout_png

    def _do() -> bytes:
        rgba = Image.open(io.BytesIO(cutout_png)).convert("RGBA")
        if mode == "512":
            out = _resize_to_box(rgba, 512)
        elif mode == "1024":
            out = _resize_to_box(rgba, 1024)
        elif mode == "square_pad_512":
            out = _square_pad(rgba, 512)
        elif mode == "square_pad_1024":
            out = _square_pad(rgba, 1024)
        else:
            return cutout_png
        buf = io.BytesIO()
        out.save(buf, format="PNG")
        return buf.getvalue()

    return await asyncio.to_thread(_do)


async def compose_result(
    cutout_png: bytes,
    bg_color: str | None = None,
    bg_image_bytes: bytes | None = None,
    size_mode: str = "original",
) -> bytes:
    """Применяет к cutout (RGBA) сначала размер, потом фон. Возвращает PNG."""
    def _do() -> bytes:
        rgba = Image.open(io.BytesIO(cutout_png)).convert("RGBA")
        # сначала ресайз
        if size_mode == "512":
            rgba = _resize_to_box(rgba, 512)
        elif size_mode == "1024":
            rgba = _resize_to_box(rgba, 1024)
        elif size_mode == "square_pad_512":
            rgba = _square_pad(rgba, 512)
        elif size_mode == "square_pad_1024":
            rgba = _square_pad(rgba, 1024)
        # потом фон
        if bg_image_bytes:
            out = _apply_image_bg(rgba, bg_image_bytes)
        elif bg_color and bg_color != "transparent":
            out = _apply_solid_bg(rgba, bg_color)
        else:
            out = rgba
        buf = io.BytesIO()
        out.save(buf, format="PNG")
        return buf.getvalue()

    return await asyncio.to_thread(_do)


def classify_error(exc: Exception) -> str:
    """Классификатор ошибок для i18n-ответов"""
    if isinstance(exc, FileTooLargeError):
        return "file_too_large"
    if isinstance(exc, ResolutionTooLargeError):
        return "resolution_too_large"
    if isinstance(exc, InvalidImageError):
        return "invalid_image"
    if isinstance(exc, ProcessingError):
        return "processing_failed"
    if isinstance(exc, asyncio.TimeoutError):
        return "timeout"
    return "unknown"
