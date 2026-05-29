from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.locales import T


def plans_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=T["btn_buy_premium"], callback_data="plan:buy:premium")],
        [InlineKeyboardButton(text=T["btn_buy_premium_plus"], callback_data="plan:buy:premium_plus")],
    ])
