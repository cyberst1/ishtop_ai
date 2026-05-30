from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.locales import T


def profile_kb(saved_count: int = 0) -> InlineKeyboardMarkup:
    rows = []
    if saved_count > 0:
        rows.append([InlineKeyboardButton(
            text=T["btn_view_saved"].format(count=saved_count),
            callback_data="profile:saved",
        )])
    rows.extend([
        [InlineKeyboardButton(text=T["btn_invite"], callback_data="profile:invite")],
        [InlineKeyboardButton(text=T["btn_plans"], callback_data="profile:plans")],
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)
