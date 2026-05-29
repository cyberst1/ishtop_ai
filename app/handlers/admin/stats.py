from __future__ import annotations

from aiogram import Dispatcher, F, Router
from aiogram.types import CallbackQuery

from app.database.engine import get_db
from app.database.repositories import (
    ReferralsRepo, SearchesRepo, SubscriptionsRepo, UsersRepo,
)
from app.locales import T
from app.security.sessions import AdminSessions

router = Router(name="admin_stats")


@router.callback_query(F.data == "adm:stats")
async def show_stats(cb: CallbackQuery) -> None:
    if not AdminSessions.is_valid(cb.from_user.id):
        await cb.answer(T["admin_session_expired"], show_alert=True)
        return
    db = get_db()
    total = await UsersRepo.total_count()
    active = await UsersRepo.active_count(7)
    premium = await SubscriptionsRepo.count_premium()
    searches = await SearchesRepo.total()
    refs = await ReferralsRepo.total()
    ai = (await db.fetchone("SELECT COUNT(*) AS c FROM ai_logs"))["c"]
    coins_spent = (await db.fetchone(
        "SELECT COALESCE(SUM(-delta), 0) AS s FROM balances WHERE delta < 0"
    ))["s"]
    text = (
        "📊 *Statistika*\n\n"
        f"👥 Jami userlar: *{total}*\n"
        f"🟢 Faol (7 kun): *{active}*\n"
        f"⭐ Premium: *{premium}*\n"
        f"🔍 Qidiruvlar: *{searches}*\n"
        f"🧠 AI so‘rovlari: *{ai}*\n"
        f"🪙 Sarflangan coin: *{round(coins_spent,2)}*\n"
        f"👥 Referrallar: *{refs}*"
    )
    await cb.message.edit_text(text)
    await cb.answer()


def register(dp: Dispatcher) -> None:
    dp.include_router(router)
