from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.locales import T


def admin_main_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=T["btn_admin_users"], callback_data="adm:users"),
            InlineKeyboardButton(text=T["btn_admin_blocks"], callback_data="adm:blocks"),
        ],
        [
            InlineKeyboardButton(text=T["btn_admin_plans"], callback_data="adm:plans"),
            InlineKeyboardButton(text=T["btn_admin_balance"], callback_data="adm:balance"),
        ],
        [
            InlineKeyboardButton(text=T["btn_admin_bonus"], callback_data="adm:bonus"),
            InlineKeyboardButton(text=T["btn_admin_broadcast"], callback_data="adm:bcast"),
        ],
        [
            InlineKeyboardButton(text=T["btn_admin_stats"], callback_data="adm:stats"),
            InlineKeyboardButton(text=T["btn_admin_settings"], callback_data="adm:settings"),
        ],
        [
            InlineKeyboardButton(text=T["btn_admin_security"], callback_data="adm:security"),
            InlineKeyboardButton(text=T["btn_admin_logs"], callback_data="adm:logs"),
        ],
    ])


def admin_user_card_kb(user_id: int, blocked: bool) -> InlineKeyboardMarkup:
    block_btn = InlineKeyboardButton(
        text=("✅ Unblock" if blocked else "🚫 Block"),
        callback_data=f"adm:user:{'unblock' if blocked else 'block'}:{user_id}",
    )
    return InlineKeyboardMarkup(inline_keyboard=[
        [block_btn],
        [
            InlineKeyboardButton(text="⭐ Tarif berish", callback_data=f"adm:user:plan:{user_id}"),
            InlineKeyboardButton(text="🪙 Balans +", callback_data=f"adm:user:balance:{user_id}"),
        ],
        [InlineKeyboardButton(text=T["back"], callback_data="adm:users")],
    ])


def admin_back_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=T["back"], callback_data="adm:home")],
    ])
