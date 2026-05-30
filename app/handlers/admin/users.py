"""
Admin user management — accepts plain text search anywhere in admin chat.

Search by:
  • Numeric ID:     8392229980
  • Username:       @ishtop_admin   (or just ishtop_admin)
  • /find prefix:   /find @username  (legacy)
"""
from __future__ import annotations

import re

from aiogram import Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from app.config import settings
from app.database.repositories import (
    AdminLogsRepo, JobsRepo, UsersRepo,
)
from app.keyboards.admin import admin_back_kb, admin_plan_pick_kb, admin_user_card_kb
from app.locales import T
from app.security.markdown import md_escape
from app.security.sessions import AdminSessions
from app.services.subscriptions import SubscriptionService

router = Router(name="admin_users")


def _guard(uid: int) -> bool:
    return AdminSessions.is_valid(uid)


_PLAN_LABEL = {"free": "Free", "premium": "Premium", "premium_plus": "Premium+"}

_USERNAME_RE = re.compile(r"^@?[A-Za-z][A-Za-z0-9_]{4,31}$")
_USER_ID_RE = re.compile(r"^\d{5,15}$")


@router.callback_query(F.data == "adm:users")
async def show_users_help(cb: CallbackQuery) -> None:
    if not _guard(cb.from_user.id):
        await cb.answer(T["admin_session_expired"], show_alert=True)
        return
    rows = await UsersRepo.list_paginated(0, 10)
    lines = [T["admin_users_help"], ""]
    if rows:
        lines.append("📋 *Oxirgi 10 ta foydalanuvchi:*")
        for r in rows:
            uname = f"@{r['username']}" if r["username"] else "—"
            lines.append(
                f"`{r['user_id']}` · {md_escape(uname)} · "
                f"{_PLAN_LABEL.get(r['plan'], r['plan'])} · 🪙 {round(r['coin_balance'], 2)}"
            )
    await cb.message.edit_text("\n".join(lines), reply_markup=admin_back_kb())
    await cb.answer()


# Plain text search — only fires if the message looks like a user ID or @username
# AND the sender is an authenticated admin.
def _looks_like_user_query(text: str) -> bool:
    text = (text or "").strip()
    return bool(_USER_ID_RE.match(text) or _USERNAME_RE.match(text))


@router.message(F.text.func(_looks_like_user_query))
async def text_search_user(message: Message) -> None:
    if message.from_user.id not in settings.admin_ids:
        return
    if not _guard(message.from_user.id):
        return
    await _do_find(message, message.text.strip())


@router.message(Command("find"))
async def find_user_cmd(message: Message) -> None:
    if not _guard(message.from_user.id):
        return
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) < 2:
        await message.answer(T["admin_users_help"])
        return
    await _do_find(message, parts[1].strip())


async def _do_find(message: Message, q: str) -> None:
    user = None
    if q.startswith("@") or not q.lstrip("-").isdigit():
        user = await UsersRepo.get_by_username(q)
    else:
        try:
            user = await UsersRepo.get(int(q))
        except ValueError:
            user = None
    if not user:
        await message.answer(T["admin_user_not_found"], reply_markup=admin_back_kb())
        return
    await _send_user_card(message, user)


async def _send_user_card(target, user) -> None:
    referrals = await UsersRepo.count_referrals(user["user_id"])
    saved = await JobsRepo.saved_count(user["user_id"])
    text = T["admin_user_card"].format(
        user_id=user["user_id"],
        username=("@" + user["username"]) if user["username"] else "—",
        full_name=md_escape(user["full_name"] or "—"),
        plan=_PLAN_LABEL.get(user["plan"], user["plan"]),
        coins=round(user["coin_balance"], 2),
        referrals=referrals,
        saved=saved,
        registered=user["created_at"],
        block_status=("🚫 Bloklangan" if user["is_blocked"] else "✅ Faol"),
    )
    kb = admin_user_card_kb(user["user_id"], bool(user["is_blocked"]))
    if isinstance(target, Message):
        await target.answer(text, reply_markup=kb)
    else:
        try:
            await target.message.edit_text(text, reply_markup=kb)
        except Exception:
            await target.message.answer(text, reply_markup=kb)


# ---------- Plan grant ----------

@router.callback_query(F.data.startswith("adm:user:plan:"))
async def open_plan_picker(cb: CallbackQuery) -> None:
    if not _guard(cb.from_user.id):
        await cb.answer(T["admin_session_expired"], show_alert=True)
        return
    uid = int(cb.data.split(":")[3])
    await cb.message.answer(
        T["admin_pick_plan"].format(user_id=uid),
        reply_markup=admin_plan_pick_kb(uid),
    )
    await cb.answer()


@router.callback_query(F.data.startswith("adm:user:setplan:"))
async def grant_plan(cb: CallbackQuery) -> None:
    if not _guard(cb.from_user.id):
        await cb.answer(T["admin_session_expired"], show_alert=True)
        return
    parts = cb.data.split(":")
    uid = int(parts[3])
    plan = parts[4]
    days = 30 if plan != "free" else 365 * 10
    await SubscriptionService.activate(uid, plan, days=days, price=0,
                                       payment_id=f"admin:{cb.from_user.id}")
    await AdminLogsRepo.log(cb.from_user.id, "grant_plan",
                            target_user=uid, payload=plan)
    try:
        await cb.message.edit_text(
            T["admin_plan_granted"].format(
                user_id=uid, plan=_PLAN_LABEL.get(plan, plan), days=days,
            ),
            reply_markup=admin_back_kb(),
        )
    except Exception:
        pass
    try:
        await cb.bot.send_message(
            uid,
            T["user_plan_granted_notify"].format(
                plan=_PLAN_LABEL.get(plan, plan), days=days,
            ),
        )
    except Exception:
        pass
    await cb.answer("✅ Tarif berildi.")


def register(dp: Dispatcher) -> None:
    dp.include_router(router)
