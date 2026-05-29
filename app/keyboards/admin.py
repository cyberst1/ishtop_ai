"""
Admin keyboards — simplified to 4 sections, each clearly labeled in Uzbek.

Layout (8 buttons → 6 buttons in 3 rows of 2):

  👥 Userlar              💳 To'lovlar (N)
  📊 Statistika           📢 Xabar yuborish
  🎁 Bonus kanallar       📂 Loglar
  🔓 Chiqish
"""
from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.locales import T


def admin_main_kb(pending_payments: int = 0) -> InlineKeyboardMarkup:
    payments_label = T["btn_admin_payments"]
    if pending_payments > 0:
        payments_label = f"💳 To'lovlar ({pending_payments})"

    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=T["btn_admin_users"], callback_data="adm:users"),
            InlineKeyboardButton(text=payments_label, callback_data="adm:pay"),
        ],
        [
            InlineKeyboardButton(text=T["btn_admin_stats"], callback_data="adm:stats"),
            InlineKeyboardButton(text=T["btn_admin_broadcast"], callback_data="adm:bcast"),
        ],
        [
            InlineKeyboardButton(text=T["btn_admin_bonus"], callback_data="adm:bonus"),
            InlineKeyboardButton(text=T["btn_admin_logs"], callback_data="adm:logs"),
        ],
        [
            InlineKeyboardButton(text=T["btn_admin_logout"], callback_data="adm:logout"),
        ],
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
        [InlineKeyboardButton(text=T["back"], callback_data="adm:home")],
    ])


def admin_back_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Asosiy panel", callback_data="adm:home")],
    ])


def admin_payment_card_kb(purchase_id: int) -> InlineKeyboardMarkup:
    """Buttons for an individual pending purchase."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"adm:pay:ok:{purchase_id}"),
            InlineKeyboardButton(text="❌ Rad etish",  callback_data=f"adm:pay:no:{purchase_id}"),
        ],
        [InlineKeyboardButton(text=T["back"], callback_data="adm:pay")],
    ])


def admin_plan_pick_kb(user_id: int) -> InlineKeyboardMarkup:
    """Pick a plan to grant to a user."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🆓 Free",      callback_data=f"adm:user:setplan:{user_id}:free")],
        [InlineKeyboardButton(text="⭐ Premium",   callback_data=f"adm:user:setplan:{user_id}:premium")],
        [InlineKeyboardButton(text="💎 Premium+",  callback_data=f"adm:user:setplan:{user_id}:premium_plus")],
        [InlineKeyboardButton(text=T["cancel"],    callback_data="adm:home")],
    ])
