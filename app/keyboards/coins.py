"""Keyboards for the 'buy coins' flow."""
from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.locales import T
from app.services.coin_packages import PACKAGES


def packages_kb() -> InlineKeyboardMarkup:
    rows = []
    for pkg in PACKAGES:
        rows.append([
            InlineKeyboardButton(
                text=pkg.label,
                callback_data=f"buy:{pkg.slug}",
            )
        ])
    rows.append([InlineKeyboardButton(text=T["back"], callback_data="earn:back")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def payment_made_kb(purchase_id: int) -> InlineKeyboardMarkup:
    """After user picks a package — quick links to support + cancel."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="📞 Adminga yozish",
            url="https://t.me/cybst_academy",
        )],
        [InlineKeyboardButton(
            text="❌ Bekor qilish",
            callback_data=f"buy:cancel:{purchase_id}",
        )],
    ])
