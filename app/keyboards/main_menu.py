from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from app.locales import T


def main_menu_kb(is_premium_plus: bool = False) -> ReplyKeyboardMarkup:
    """
    Main reply keyboard. The 🧠 ISH TOP AI assistant is available to EVERYONE
    (free users get a 2-message trial), so the button is always shown.
    """
    rows = [
        [KeyboardButton(text=T["btn_search"]), KeyboardButton(text=T["btn_advisor"])],
        [KeyboardButton(text=T["btn_earn"]), KeyboardButton(text=T["btn_plans"])],
        [KeyboardButton(text=T["btn_profile"]), KeyboardButton(text=T["btn_help"])],
    ]
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True, is_persistent=True)
