"""Admin balance management — credit / debit a user with clear instructions."""
from __future__ import annotations

from aiogram import Dispatcher, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.bot.states import AdminBalanceSG
from app.database.repositories import AdminLogsRepo, UsersRepo
from app.keyboards.admin import admin_back_kb
from app.locales import T
from app.security.sessions import AdminSessions
from app.services.coin_economy import CoinEconomy

router = Router(name="admin_balance")


def _guard(uid: int) -> bool:
    return AdminSessions.is_valid(uid)


@router.callback_query(F.data.startswith("adm:user:balance:"))
async def open_balance_for(cb: CallbackQuery, state: FSMContext) -> None:
    if not _guard(cb.from_user.id):
        await cb.answer(T["admin_session_expired"], show_alert=True)
        return
    uid = int(cb.data.split(":")[3])
    await state.update_data(target_user_id=uid)
    await state.set_state(AdminBalanceSG.amount)
    await cb.message.answer(
        T["admin_balance_prompt"].format(user_id=uid),
        reply_markup=admin_back_kb(),
    )
    await cb.answer()


@router.message(AdminBalanceSG.amount, F.text)
async def take_amount(message: Message, state: FSMContext) -> None:
    if not _guard(message.from_user.id):
        return
    txt = (message.text or "").strip().replace(",", ".")
    try:
        delta = float(txt)
    except ValueError:
        await message.answer(T["admin_balance_bad_amount"])
        return

    data = await state.get_data()
    uid = data.get("target_user_id")
    if uid is None:
        await state.clear()
        return

    if not await UsersRepo.get(uid):
        await message.answer(T["admin_user_not_found"])
        await state.clear()
        return

    new_balance = await CoinEconomy.adjust(
        uid, delta,
        reason="admin_grant" if delta > 0 else "admin_remove",
        related_id=str(message.from_user.id),
    )
    await AdminLogsRepo.log(message.from_user.id, "balance_adjust",
                            target_user=uid, payload=str(delta))
    await state.clear()
    await message.answer(
        T["admin_balance_done"].format(
            user_id=uid, delta=delta, balance=round(new_balance, 2),
        ),
        reply_markup=admin_back_kb(),
    )

    # Notify user
    try:
        if delta > 0:
            await message.bot.send_message(
                uid,
                T["user_balance_credited_notify"].format(
                    delta=delta, balance=round(new_balance, 2),
                ),
            )
    except Exception:
        pass


def register(dp: Dispatcher) -> None:
    dp.include_router(router)
