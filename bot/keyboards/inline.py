"""Inline-клавиатуры — главное меню, подписка, язык, настройки"""
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.config import settings
from bot.emojis import E_ID
from bot.i18n import t


def get_start_keyboard(user_id: int, lang: str = "ru") -> InlineKeyboardMarkup:
    """Главное меню бота"""
    buttons = [
        [InlineKeyboardButton(
            text=t("btn.process", lang),
            callback_data="process_photo",
            style="primary",
            icon_custom_emoji_id=E_ID["camera"],
        )],
        [
            InlineKeyboardButton(
                text=t("btn.profile", lang),
                callback_data="my_profile",
                style="success",
                icon_custom_emoji_id=E_ID["profile"],
            ),
            InlineKeyboardButton(
                text=t("btn.help", lang),
                callback_data="help",
                style="success",
                icon_custom_emoji_id=E_ID["info"],
            ),
        ],
        [
            InlineKeyboardButton(
                text=t("btn.language", lang),
                callback_data="change_language",
                style="success",
                icon_custom_emoji_id=E_ID["language"],
            ),
            InlineKeyboardButton(
                text=t("btn.settings", lang),
                callback_data="open_settings",
                style="success",
                icon_custom_emoji_id=E_ID["edit"],
            ),
        ],
    ]

    # кнопка админки для админов
    if user_id in settings.admin_id_list:
        buttons.append([InlineKeyboardButton(
            text=t("btn.admin_panel", lang),
            callback_data="admin_panel",
            style="danger",
            icon_custom_emoji_id=E_ID["admin"],
        )])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_back_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Кнопка 'Назад' в главное меню"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=t("btn.back", lang),
            callback_data="back_to_menu",
            style="success",
            icon_custom_emoji_id=E_ID["back"],
        )],
    ])


def get_subscription_keyboard(
    channels: list[dict], lang: str = "ru"
) -> InlineKeyboardMarkup:
    """Клавиатура подписки на каналы"""
    buttons = []
    for ch in channels:
        buttons.append([InlineKeyboardButton(
            text=f"{ch['title']}",
            url=ch["invite_link"],
            style="primary",
            icon_custom_emoji_id=E_ID["megaphone"],
        )])
    buttons.append([InlineKeyboardButton(
        text=t("btn.check_sub", lang),
        callback_data="check_subscription",
        style="success",
        icon_custom_emoji_id=E_ID["check"],
    )])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_language_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора языка"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Русский",
                callback_data="set_lang_ru",
                style="primary",
                icon_custom_emoji_id=E_ID["flag_ru"],
            ),
            InlineKeyboardButton(
                text="O'zbek",
                callback_data="set_lang_uz",
                style="primary",
                icon_custom_emoji_id=E_ID["flag_uz"],
            ),
            InlineKeyboardButton(
                text="English",
                callback_data="set_lang_en",
                style="primary",
                icon_custom_emoji_id=E_ID["flag_gb"],
            ),
        ],
    ])


def get_settings_keyboard(lang: str = "ru", current_model: str = "u2net") -> InlineKeyboardMarkup:
    """Меню настроек: список моделей rembg (текущая помечена ✓) + назад"""
    models = [
        ("u2net", "btn.model_u2net"),
        ("isnet-general-use", "btn.model_isnet"),
    ]
    rows = []
    for model_key, label_key in models:
        label = t(label_key, lang)
        if model_key == current_model:
            label = "✓ " + label
        rows.append([InlineKeyboardButton(
            text=label,
            callback_data=f"set_model_{model_key}",
            style="primary",
            icon_custom_emoji_id=E_ID["gear"],
        )])
    rows.append([InlineKeyboardButton(
        text=t("btn.back", lang),
        callback_data="back_to_menu",
        style="success",
        icon_custom_emoji_id=E_ID["back"],
    )])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_result_keyboard(
    request_id: str,
    lang: str = "ru",
    current_bg: str = "transparent",
    current_size: str = "original",
) -> InlineKeyboardMarkup:
    """Кнопки под результатом: смена фона, размера. Текущее состояние пробрасывается дальше."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=t("btn.bg_change", lang),
            callback_data=f"bg_menu:{request_id}:{current_size}",
            style="primary",
            icon_custom_emoji_id=E_ID["edit"],
        )],
        [InlineKeyboardButton(
            text=t("btn.size_change", lang),
            callback_data=f"size_menu:{request_id}:{current_bg}",
            style="primary",
            icon_custom_emoji_id=E_ID["package"],
        )],
        [InlineKeyboardButton(
            text=t("btn.home", lang),
            callback_data="result_to_menu",
            style="success",
            icon_custom_emoji_id=E_ID["home"],
        )],
    ])


def get_bg_color_keyboard(
    request_id: str,
    lang: str = "ru",
    current_size: str = "original",
    current_bg: str = "transparent",
) -> InlineKeyboardMarkup:
    """Выбор фона. Текущий помечен ✓. current_size — пробрасываем в bg_apply."""
    def _label(key: str, color: str) -> str:
        text = t(key, lang)
        return ("✓ " + text) if color == current_bg else text

    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=_label("btn.bg_transparent", "transparent"),
                callback_data=f"bg_apply:{request_id}:transparent:{current_size}",
                style="primary",
            ),
            InlineKeyboardButton(
                text=_label("btn.bg_white", "white"),
                callback_data=f"bg_apply:{request_id}:white:{current_size}",
                style="primary",
            ),
        ],
        [
            InlineKeyboardButton(
                text=_label("btn.bg_black", "black"),
                callback_data=f"bg_apply:{request_id}:black:{current_size}",
                style="primary",
            ),
            InlineKeyboardButton(
                text=_label("btn.bg_green", "green"),
                callback_data=f"bg_apply:{request_id}:green:{current_size}",
                style="primary",
            ),
        ],
        [InlineKeyboardButton(
            text=t("btn.bg_image", lang),
            callback_data=f"bg_image:{request_id}:{current_size}",
            style="primary",
            icon_custom_emoji_id=E_ID["camera"],
        )],
        [InlineKeyboardButton(
            text=t("btn.back", lang),
            callback_data=f"back_result:{request_id}:{current_bg}:{current_size}",
            style="success",
            icon_custom_emoji_id=E_ID["back"],
        )],
    ])


def get_size_keyboard(
    request_id: str,
    lang: str = "ru",
    current_bg: str = "transparent",
    current_size: str = "original",
) -> InlineKeyboardMarkup:
    """Выбор размера: оригинал / 512 / 1024 / квадратный паддинг. current_bg пробрасывается."""
    def _label(key: str, mode: str) -> str:
        text = t(key, lang)
        return ("✓ " + text) if mode == current_size else text

    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=_label("btn.size_original", "original"),
                callback_data=f"size_apply:{request_id}:original:{current_bg}",
                style="primary",
            ),
            InlineKeyboardButton(
                text=_label("btn.size_512", "512"),
                callback_data=f"size_apply:{request_id}:512:{current_bg}",
                style="primary",
            ),
        ],
        [
            InlineKeyboardButton(
                text=_label("btn.size_1024", "1024"),
                callback_data=f"size_apply:{request_id}:1024:{current_bg}",
                style="primary",
            ),
            InlineKeyboardButton(
                text=_label("btn.size_square", "square_pad_512"),
                callback_data=f"size_apply:{request_id}:square_pad_512:{current_bg}",
                style="primary",
            ),
        ],
        [InlineKeyboardButton(
            text=t("btn.back", lang),
            callback_data=f"back_result:{request_id}:{current_bg}:{current_size}",
            style="success",
            icon_custom_emoji_id=E_ID["back"],
        )],
    ])
