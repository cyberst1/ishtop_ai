"""
Admin reply-button router.

Maps the 7 main admin actions (USERLAR / OBUNA / TA'RIF NARXLARINI ... /
BLOKLASH / XABAR YUBORISH / STATISTIKA / BONUS KANALLAR) — each triggered
by its reply-keyboard text — to the corresponding flow.

This router is registered FIRST among admin handlers so its text matches
beat any FSM-state filters elsewhere.
"""
from __future__ import annotations

from aiogram import Bot, Dispatcher, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.bot.states import AdminBlockSG, AdminBroadcastSG, AdminPriceSG
from app.config import settings
from app.database.repositories import (
    AdminLogsRepo, BlocksRepo, BonusRepo, CoinPurchasesRepo, UsersRepo,
)
from app.keyboards.admin import (
    BTN_BCAST, BTN_BLOCK, BTN_BONUS, BTN_LOGOUT, BTN_PRICES, BTN_STATS,
    BTN_SUBS, BTN_USERS, admin_back_kb, admin_prices_kb, admin_reply_kb,
    remove_kb,
)
from app.locales import T
from app.security.markdown import md_escape
from app.security.sessions import AdminSessions
from app.services.runtime_config import EDITABLE_KEYS, runtime

router = Router(name="admin_menu")


def _is_session(uid: int) -> bool:
    return AdminSessions.is_valid(uid)


# Helper: only react to admin reply-keyboard buttons when admin is logged in
def _admin_only(uid: int) -> bool:
    return uid in settings.admin_ids and _is_session(uid)


# ---------------------------------------------------------------- USERLAR

@router.message(F.text == BTN_USERS)
async def open_users(message: Message, state: FSMContext) -> None:
    if not _admin_only(message.from_user.id):
        return
    await state.clear()
    rows = await UsersRepo.list_paginated(0, 10)
    lines = [T["admin_users_help"], ""]
    if rows:
        lines.append("📋 *Oxirgi 10 ta foydalanuvchi:*")
        plan_label = {"free": "Free", "premium": "Premium", "premium_plus": "Premium+"}
        for r in rows:
            uname = f"@{r['username']}" if r["username"] else "—"
            lines.append(
                f"`{r['user_id']}` · {md_escape(uname)} · "
                f"{plan_label.get(r['plan'], r['plan'])} · "
                f"🪙 {round(r['coin_balance'], 2)}"
            )
    await message.answer("\n".join(lines))


# ---------------------------------------------------------------- OBUNA

@router.message(F.text.startswith(BTN_SUBS))
async def open_subscriptions(message: Message, state: FSMContext, bot: Bot) -> None:
    if not _admin_only(message.from_user.id):
        return
    await state.clear()

    # Always show 'Userga tarif ulash' action header
    from app.keyboards.admin import admin_subs_action_kb
    await message.answer(T["admin_subs_header"], reply_markup=admin_subs_action_kb())

    rows = await CoinPurchasesRepo.list_pending(20)
    if not rows:
        await message.answer(T["admin_payments_empty"])
        return

    await message.answer(T["admin_payments_header"].format(count=len(rows)))

    from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
    for r in rows:
        uname = f"@{r['username']}" if r["username"] else "—"
        full_name = md_escape(r["full_name"] or "—")
        price = f"{r['price']:,}".replace(",", " ")
        body = (
            f"💳 *So'rov #{r['id']}*\n\n"
            f"👤 {full_name} · {md_escape(uname)}\n"
            f"🆔 `{r['user_id']}`\n"
            f"🪙 *{r['coins']} coin* uchun\n"
            f"💵 *{price} so'm*\n"
            f"📅 {r['created_at']}"
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"adm:pay:ok:{r['id']}"),
            InlineKeyboardButton(text="❌ Rad etish",  callback_data=f"adm:pay:no:{r['id']}"),
        ]])
        try:
            await message.answer(body, reply_markup=kb)
        except Exception:
            pass


# ---------------------------------------------------------------- TA'RIF NARXLARI

@router.message(F.text == BTN_PRICES)
async def open_prices(message: Message, state: FSMContext) -> None:
    if not _admin_only(message.from_user.id):
        return
    await state.clear()
    lines = ["💰 *TA'RIF NARXLARI VA EKONOMIKA*\n", "Joriy qiymatlar:\n"]
    for key in EDITABLE_KEYS:
        val = getattr(runtime, key)
        lines.append(f"  • {runtime.label(key)}: *{val}*")
    lines.append("\nO'zgartirish uchun pastdagi tugmalardan birini bosing 👇")
    await message.answer("\n".join(lines), reply_markup=admin_prices_kb())


# ---------------------------------------------------------------- BLOKLASH

@router.message(F.text == BTN_BLOCK)
async def open_block(message: Message, state: FSMContext) -> None:
    if not _admin_only(message.from_user.id):
        return
    await state.clear()
    await state.set_state(AdminBlockSG.user_input)
    await message.answer(T["admin_block_prompt"])


@router.message(AdminBlockSG.user_input, F.text)
async def block_apply(message: Message, state: FSMContext) -> None:
    if not _admin_only(message.from_user.id):
        await state.clear()
        return

    q = (message.text or "").strip()
    if q in (BTN_LOGOUT,):  # safety — let logout text exit
        await state.clear()
        return

    user = None
    if q.startswith("@") or not q.lstrip("-").isdigit():
        user = await UsersRepo.get_by_username(q)
    else:
        try:
            user = await UsersRepo.get(int(q))
        except ValueError:
            user = None

    if not user:
        await message.answer(T["admin_user_not_found"])
        await state.clear()
        return

    new_blocked = not bool(user["is_blocked"])
    await UsersRepo.set_block(user["user_id"], new_blocked,
                              "admin_block" if new_blocked else None)
    await BlocksRepo.add(user["user_id"], message.from_user.id,
                         "block" if new_blocked else "unblock", None)
    await AdminLogsRepo.log(message.from_user.id,
                            "block" if new_blocked else "unblock",
                            target_user=user["user_id"])
    await state.clear()

    flag = "🚫 BLOKLANDI" if new_blocked else "✅ BLOKDAN CHIQARILDI"
    await message.answer(
        T["admin_block_done"].format(
            flag=flag,
            user_id=user["user_id"],
            username=("@" + user["username"]) if user["username"] else "—",
        )
    )


# ---------------------------------------------------------------- XABAR YUBORISH

@router.message(F.text == BTN_BCAST)
async def open_broadcast(message: Message, state: FSMContext) -> None:
    if not _admin_only(message.from_user.id):
        return
    await state.clear()
    await state.set_state(AdminBroadcastSG.text)
    await message.answer(T["admin_broadcast_prompt"])


# ---------------------------------------------------------------- STATISTIKA

@router.message(F.text == BTN_STATS)
async def open_stats(message: Message, state: FSMContext) -> None:
    if not _admin_only(message.from_user.id):
        return
    await state.clear()
    # Reuse the dashboard text from login
    from app.handlers.admin.login import _build_dashboard
    text, _ = await _build_dashboard()
    await message.answer(text)


# ---------------------------------------------------------------- BONUS KANALLAR

@router.message(F.text == BTN_BONUS)
async def open_bonus(message: Message, state: FSMContext) -> None:
    if not _admin_only(message.from_user.id):
        return
    await state.clear()
    rows = await BonusRepo.list_all()
    lines = ["🎁 *Bonus kanallar*\n"]
    if not rows:
        lines.append("Hozircha kanallar yo'q.")
    else:
        for r in rows:
            flag = "🟢" if r["enabled"] else "⚪"
            lines.append(
                f"{flag} `{r['id']}` · {md_escape(r['title'])} · +{r['reward']} coin"
            )
    lines.append("\n*Buyruqlar:*")
    lines.append("  • `/bonus_add`             — yangi kanal qo'shish")
    lines.append("  • `/bonus_del <id>`        — kanalni o'chirish")
    await message.answer("\n".join(lines))


# ---------------------------------------------------------------- CHIQISH

@router.message(F.text == BTN_LOGOUT)
async def logout(message: Message, state: FSMContext) -> None:
    if message.from_user.id not in settings.admin_ids:
        return
    AdminSessions.revoke(message.from_user.id)
    await AdminLogsRepo.log(message.from_user.id, "logout", success=True)
    await state.clear()
    await message.answer(T["admin_logged_out"], reply_markup=remove_kb())


def register(dp: Dispatcher) -> None:
    dp.include_router(router)
