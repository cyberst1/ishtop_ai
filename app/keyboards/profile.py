from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.locales import T


def profile_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=T["btn_invite"], callback_data="profile:invite")],
        [InlineKeyboardButton(text=T["btn_plans"], callback_data="profile:plans")],
    ])
