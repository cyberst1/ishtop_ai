"""/admin_kirish — bcrypt password + session + simple panel."""
from __future__ import annotations

from aiogram import Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.bot.states import AdminLoginSG
from app.config import settings
from app.database.repositories import AdminLogsRepo, CoinPurchasesRepo
from app.keyboards import admin_main_kb
from app.locales import T
from app.security.passwords import verify_admin
from app.security.sessions import AdminSessions
from app.utils.logger import logger

router = Router(name="admin_login")


def _is_admin(user_id: int) -> bool:
    return user_id in settings.admin_ids


async def _send_panel(target, *, edit: bool = False) -> None:
    """Render the home admin panel (with pending-payments badge)."""
    pending = await CoinPurchasesRepo.count_pending()
    text = T["admin_panel_text"].format(pending=pending)
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


@router.message(Command("admin_kirish"))
async def cmd_admin_login(message: Message, state: FSMContext) -> None:
    if not _is_admin(message.from_user.id):
        await message.answer(T["admin_not_allowed"])
        await AdminLogsRepo.log(message.from_user.id, "login_attempt_not_admin", success=False)
        return

    # Already logged in? Skip password.
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
        await message.delete()  # remove the password from chat
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
