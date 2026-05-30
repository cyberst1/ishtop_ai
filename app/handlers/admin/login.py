"""/admin_kirish — bcrypt password + session + rich dashboard."""
from __future__ import annotations

from aiogram import Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.bot.states import AdminLoginSG
from app.config import settings
from app.database.engine import get_db
from app.database.repositories import (
    AdminLogsRepo, CoinPurchasesRepo, SearchesRepo,
    SubscriptionsRepo, UsersRepo,
)
from app.keyboards import admin_main_kb
from app.locales import T
from app.security.passwords import verify_admin
from app.security.sessions import AdminSessions
from app.utils.logger import logger

router = Router(name="admin_login")


def _is_admin(user_id: int) -> bool:
    return user_id in settings.admin_ids


# ---------- dashboard ----------

async def _build_dashboard() -> tuple[str, int]:
    """Return (formatted_dashboard_text, pending_payments_count)."""
    db = get_db()

    total_users     = await UsersRepo.total_count()
    active_7d       = await UsersRepo.active_count(7)
    premium_count   = await SubscriptionsRepo.count_premium()
    pending_pay     = await CoinPurchasesRepo.count_pending()
    searches_total  = await SearchesRepo.total()

    today_searches = (await db.fetchone(
        "SELECT COUNT(*) AS c FROM searches WHERE date(created_at) = date('now')"
    ))["c"]
    today_signups = (await db.fetchone(
        "SELECT COUNT(*) AS c FROM users WHERE date(created_at) = date('now')"
    ))["c"]
    today_revenue = (await db.fetchone(
        """SELECT COALESCE(SUM(price), 0) AS s FROM coin_purchases
           WHERE status = 'confirmed' AND date(confirmed_at) = date('now')"""
    ))["s"]
    total_revenue = await CoinPurchasesRepo.total_revenue()
    coins_spent = (await db.fetchone(
        "SELECT COALESCE(SUM(-delta), 0) AS s FROM balances WHERE delta < 0"
    ))["s"]

    text = T["admin_dashboard"].format(
        total_users=total_users,
        active_7d=active_7d,
        today_signups=today_signups,
        premium_count=premium_count,
        searches_total=searches_total,
        today_searches=today_searches,
        coins_spent=round(coins_spent, 2),
        today_revenue=f"{today_revenue:,}".replace(",", " "),
        total_revenue=f"{total_revenue:,}".replace(",", " "),
        pending=pending_pay,
    )
    return text, pending_pay


async def _send_panel(target, *, edit: bool = False) -> None:
    text, pending = await _build_dashboard()
    kb = admin_main_kb(pending_payments=pending)
    if edit and isinstance(target, CallbackQuery):
        try:
            await target.message.edit_text(text, reply_markup=kb)
            return
        except Exception:
            pass
    if isinstance(target, Message):
        await target.answer(text, reply_markup=kb)
    elif isinstance(target, CallbackQuery):
        await target.message.answer(text, reply_markup=kb)


# ---------- login ----------

@router.message(Command("admin_kirish"))
async def cmd_admin_login(message: Message, state: FSMContext) -> None:
    if not _is_admin(message.from_user.id):
        await message.answer(T["admin_not_allowed"])
        await AdminLogsRepo.log(message.from_user.id, "login_attempt_not_admin", success=False)
        return

    if AdminSessions.is_valid(message.from_user.id):
        await _send_panel(message)
        return

    await state.set_state(AdminLoginSG.password)
    await message.answer(T["admin_password_prompt"])


@router.message(AdminLoginSG.password, F.text)
async def check_password(message: Message, state: FSMContext) -> None:
    if not _is_admin(message.from_user.id):
        await state.clear()
        return
    pwd = (message.text or "").strip()
    try:
        await message.delete()
    except Exception:
        pass

    ok = verify_admin(
        pwd,
        hashed=settings.admin_password_hash,
        plaintext=settings.admin_password,
    )
    if not ok:
        await AdminLogsRepo.log(message.from_user.id, "login_wrong_password", success=False)
        logger.warning("admin.login.wrong", extra={"admin_id": message.from_user.id})
        await message.answer(T["admin_password_wrong"])
        return

    AdminSessions.create(message.from_user.id)
    await AdminLogsRepo.log(message.from_user.id, "login_ok", success=True)
    await state.clear()
    await message.answer(T["admin_login_ok"])
    await _send_panel(message)


@router.message(Command("admin_menu"))
async def cmd_admin_menu(message: Message) -> None:
    """Quick shortcut to open admin home if session is valid."""
    if not AdminSessions.is_valid(message.from_user.id):
        await message.answer(T["admin_session_expired"])
        return
    await _send_panel(message)


@router.callback_query(F.data == "adm:home")
async def adm_home(cb: CallbackQuery) -> None:
    if not AdminSessions.is_valid(cb.from_user.id):
        await cb.answer(T["admin_session_expired"], show_alert=True)
        return
    await _send_panel(cb, edit=True)
    await cb.answer()


@router.callback_query(F.data == "adm:logout")
async def adm_logout(cb: CallbackQuery) -> None:
    AdminSessions.revoke(cb.from_user.id)
    await AdminLogsRepo.log(cb.from_user.id, "logout", success=True)
    try:
        await cb.message.edit_text(T["admin_logged_out"])
    except Exception:
        pass
    await cb.answer("👋 Chiqildi.")


def register(dp: Dispatcher) -> None:
    dp.include_router(router)
