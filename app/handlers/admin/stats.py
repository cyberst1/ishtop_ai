"""Admin: detailed statistics — users / revenue / activity."""
from __future__ import annotations

from aiogram import Dispatcher, F, Router
from aiogram.types import CallbackQuery

from app.database.engine import get_db
from app.database.repositories import (
    CoinPurchasesRepo, ReferralsRepo, SearchesRepo,
    SubscriptionsRepo, UsersRepo,
)
from app.keyboards.admin import admin_back_kb
from app.locales import T
from app.security.sessions import AdminSessions

router = Router(name="admin_stats")


@router.callback_query(F.data == "adm:stats")
async def show_stats(cb: CallbackQuery) -> None:
    if not AdminSessions.is_valid(cb.from_user.id):
        await cb.answer(T["admin_session_expired"], show_alert=True)
        return

    db = get_db()
    total_users   = await UsersRepo.total_count()
    active_1d     = await UsersRepo.active_count(1)
    active_7d     = await UsersRepo.active_count(7)
    active_30d    = await UsersRepo.active_count(30)
    premium_count = await SubscriptionsRepo.count_premium()
    searches      = await SearchesRepo.total()
    refs          = await ReferralsRepo.total()
    today_revenue = (await db.fetchone(
        """SELECT COALESCE(SUM(price), 0) AS s FROM coin_purchases
           WHERE status='confirmed' AND date(confirmed_at) = date('now')"""
    ))["s"]
    week_revenue = (await db.fetchone(
        """SELECT COALESCE(SUM(price), 0) AS s FROM coin_purchases
           WHERE status='confirmed' AND confirmed_at > datetime('now','-7 days')"""
    ))["s"]
    total_revenue = await CoinPurchasesRepo.total_revenue()
    purchases_total = (await db.fetchone(
        "SELECT COUNT(*) AS c FROM coin_purchases WHERE status='confirmed'"
    ))["c"]
    ai_calls = (await db.fetchone(
        "SELECT COUNT(*) AS c FROM ai_logs"
    ))["c"]
    coins_spent = (await db.fetchone(
        "SELECT COALESCE(SUM(-delta), 0) AS s FROM balances WHERE delta < 0"
    ))["s"]
    coins_credited = (await db.fetchone(
        "SELECT COALESCE(SUM(delta), 0) AS s FROM balances WHERE delta > 0"
    ))["s"]
    today_signups = (await db.fetchone(
        "SELECT COUNT(*) AS c FROM users WHERE date(created_at) = date('now')"
    ))["c"]
    blocked = (await db.fetchone(
        "SELECT COUNT(*) AS c FROM users WHERE is_blocked = 1"
    ))["c"]

    text = T["admin_stats_full"].format(
        total_users=total_users,
        active_1d=active_1d,
        active_7d=active_7d,
        active_30d=active_30d,
        today_signups=today_signups,
        blocked=blocked,
        premium_count=premium_count,
        searches=searches,
        refs=refs,
        ai_calls=ai_calls,
        coins_spent=round(coins_spent, 2),
        coins_credited=round(coins_credited, 2),
        purchases_total=purchases_total,
        today_revenue=f"{today_revenue:,}".replace(",", " "),
        week_revenue=f"{week_revenue:,}".replace(",", " "),
        total_revenue=f"{total_revenue:,}".replace(",", " "),
    )
    try:
        await cb.message.edit_text(text, reply_markup=admin_back_kb())
    except Exception:
        await cb.message.answer(text, reply_markup=admin_back_kb())
    await cb.answer()


def register(dp: Dispatcher) -> None:
    dp.include_router(router)
