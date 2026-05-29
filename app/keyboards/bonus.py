from typing import Iterable

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.locales import T


def earn_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=T["btn_invite"], callback_data="earn:invite")],
        [InlineKeyboardButton(text=T["btn_bonus_channels"], callback_data="earn:bonus")],
        [InlineKeyboardButton(text=T["btn_buy_coins"], callback_data="earn:buy")],
    ])


def bonus_channels_kb(channels: Iterable) -> InlineKeyboardMarkup:
    rows = []
    for ch in channels:
        rows.append([
            InlineKeyboardButton(text=f"🔗 {ch['title']}", url=ch["invite_link"]),
            InlineKeyboardButton(text=T["bonus_check_btn"], callback_data=f"bonus:check:{ch['id']}"),
        ])
    return InlineKeyboardMarkup(inline_keyboard=rows or [
        [InlineKeyboardButton(text=T["back"], callback_data="earn:back")]
    ])
