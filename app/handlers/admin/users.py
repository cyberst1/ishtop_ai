"""Admin: user list, search by id/username, user card."""
from __future__ import annotations

from aiogram import Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from app.database.repositories import JobsRepo, UsersRepo
from app.keyboards import admin_user_card_kb
from app.locales import T
from app.security.sessions import AdminSessions
from app.security.markdown import md_escape

router = Router(name="admin_users")


def _guard(uid: int) -> bool:
    return AdminSessions.is_valid(uid)


@router.callback_query(F.data == "adm:users")
async def list_users(cb: CallbackQuery) -> None:
    if not _guard(cb.from_user.id):
        await cb.answer(T["admin_session_expired"], show_alert=True)
        return
    rows = await UsersRepo.list_paginated(0, 20)
    lines = ["👥 *Userlar (oxirgi 20):*\n"]
    for r in rows:
        uname = f"@{r['username']}" if r["username"] else "—"
        lines.append(f"`{r['user_id']}` · {md_escape(uname)} · {r['plan']} · 🪙 {round(r['coin_balance'],2)}")
    lines.append("\n🔎 Qidirish: `/find <id|@username>`")
    await cb.message.edit_text("\n".join(lines))
    await cb.answer()


@router.message(Command("find"))
async def find_user(message: Message) -> None:
    if not _guard(message.from_user.id):
        return
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Foydalanish: `/find 123456789` yoki `/find @username`")
        return
    q = parts[1].strip()
    user = None
    if q.startswith("@") or not q.isdigit():
        user = await UsersRepo.get_by_username(q)
    else:
        user = await UsersRepo.get(int(q))
    if not user:
        await message.answer("❌ User topilmadi.")
        return
    referrals = await UsersRepo.count_referrals(user["user_id"])
    saved = await JobsRepo.saved_count(user["user_id"])
    text = (
        "👤 *USER INFO*\n\n"
        f"🆔 ID: `{user['user_id']}`\n"
        f"👤 Username: {('@' + user['username']) if user['username'] else '—'}\n"
        f"⭐ Tarif: {user['plan']}\n"
        f"🪙 Coin: {round(user['coin_balance'],2)}\n"
        f"👥 Referal: {referrals}\n"
        f"❤️ Saqlangan: {saved}\n"
        f"📅 Ro‘yxat: {user['created_at']}\n"
        f"🚫 Block: {'ha' if user['is_blocked'] else 'yo‘q'}"
    )
    await message.answer(text, reply_markup=admin_user_card_kb(user["user_id"], bool(user["is_blocked"])))


def register(dp: Dispatcher) -> None:
    dp.include_router(router)
