from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from app.locales import T


def main_menu_kb(is_premium_plus: bool = False) -> ReplyKeyboardMarkup:
    rows = [
        [KeyboardButton(text=T["btn_search"]), KeyboardButton(text=T["btn_earn"])],
        [KeyboardButton(text=T["btn_plans"]), KeyboardButton(text=T["btn_profile"])],
        [KeyboardButton(text=T["btn_help"])],
    ]
    if is_premium_plus:
        rows.insert(2, [KeyboardButton(text=T["btn_advisor"])])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)
