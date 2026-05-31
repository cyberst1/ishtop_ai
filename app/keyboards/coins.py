"""Keyboards for the coin-packages info screen (display only)."""
from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.locales import T
from app.services.coin_packages import PACKAGES


def packages_kb() -> InlineKeyboardMarkup:
    rows = []
    for pkg in PACKAGES:
        rows.append([
            InlineKeyboardButton(text=pkg.label, callback_data=f"buy:{pkg.slug}")
        ])
    rows.append([InlineKeyboardButton(text=T["back"], callback_data="earn:back")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
