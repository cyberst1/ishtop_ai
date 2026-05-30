"""
Admin keyboards.

Primary admin UI is now a *reply keyboard* (custom buttons next to the input
field), exactly as requested by the product owner. Inline keyboards are still
used inside cards (user card, payment card, plan picker) for per-row actions.
"""
from __future__ import annotations

from aiogram.types import (
    InlineKeyboardButton, InlineKeyboardMarkup,
    KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove,
)

from app.locales import T


# ---------------- main reply keyboard ----------------

# Button labels — kept in one place and exported for use in F.text filters
BTN_USERS    = "👥 USERLAR"
BTN_SUBS     = "💳 OBUNA"
BTN_PRICES   = "💰 TA'RIF NARXLARINI O'ZGARTIRISH"
BTN_BLOCK    = "🚫 BLOKLASH"
BTN_BCAST    = "📢 XABAR YUBORISH"
BTN_STATS    = "📊 STATISTIKA"
BTN_BONUS    = "🎁 BONUS KANALLAR"
BTN_LOGOUT   = "🔓 CHIQISH"

ALL_ADMIN_BUTTONS = {
    BTN_USERS, BTN_SUBS, BTN_PRICES, BTN_BLOCK,
    BTN_BCAST, BTN_STATS, BTN_BONUS, BTN_LOGOUT,
}


def admin_reply_kb(pending_payments: int = 0) -> ReplyKeyboardMarkup:
    """The persistent admin reply keyboard. Pending count is added to OBUNA."""
    subs = BTN_SUBS if pending_payments == 0 else f"{BTN_SUBS} ({pending_payments})"
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_USERS),  KeyboardButton(text=subs)],
            [KeyboardButton(text=BTN_PRICES)],
            [KeyboardButton(text=BTN_BLOCK),  KeyboardButton(text=BTN_BCAST)],
            [KeyboardButton(text=BTN_STATS),  KeyboardButton(text=BTN_BONUS)],
            [KeyboardButton(text=BTN_LOGOUT)],
        ],
        resize_keyboard=True,
        is_persistent=True,
        input_field_placeholder="Admin amalini tanlang yoki ID/username yozing...",
    )


def remove_kb() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()


# ---------------- inline keyboards (cards) ----------------

def admin_back_kb() -> InlineKeyboardMarkup:
    """Used at the bottom of result/info screens. Reply kb stays anyway."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Asosiy panel", callback_data="adm:home")],
    ])


def admin_user_card_kb(user_id: int, blocked: bool) -> InlineKeyboardMarkup:
    block_btn = InlineKeyboardButton(
        text=("✅ Blokdan chiqarish" if blocked else "🚫 Bloklash"),
        callback_data=f"adm:user:{'unblock' if blocked else 'block'}:{user_id}",
    )
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🪙 Coin qo'shish", callback_data=f"adm:user:balance:{user_id}"),
            InlineKeyboardButton(text="⭐ Tarif berish", callback_data=f"adm:user:plan:{user_id}"),
        ],
        [block_btn],
    ])


def admin_plan_pick_kb(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🆓 Free",      callback_data=f"adm:user:setplan:{user_id}:free")],
        [InlineKeyboardButton(text="⭐ Premium",   callback_data=f"adm:user:setplan:{user_id}:premium")],
        [InlineKeyboardButton(text="💎 Premium+",  callback_data=f"adm:user:setplan:{user_id}:premium_plus")],
        [InlineKeyboardButton(text=T["cancel"],    callback_data="adm:cancel_plan")],
    ])


def admin_subs_action_kb() -> InlineKeyboardMarkup:
    """Header action shown above the pending-payments list inside OBUNA."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Userga tarif ulash",
                              callback_data="adm:grant_plan_start")],
    ])


def admin_prices_kb() -> InlineKeyboardMarkup:
    """Inline picker for which setting to edit."""
    from app.services.runtime_config import EDITABLE_KEYS, LABELS
    rows = []
    for key in EDITABLE_KEYS:
        rows.append([InlineKeyboardButton(
            text=LABELS[key], callback_data=f"adm:price:edit:{key}",
        )])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ---------------- legacy (kept for any external reference) ----------------

def admin_main_kb(pending_payments: int = 0) -> InlineKeyboardMarkup:
    """DEPRECATED — superseded by admin_reply_kb. Kept to avoid import errors."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=BTN_USERS, callback_data="adm:users"),
         InlineKeyboardButton(text=BTN_SUBS, callback_data="adm:pay")],
    ])
