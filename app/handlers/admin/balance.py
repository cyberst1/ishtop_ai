"""Admin balance management — credit / debit a user with clear instructions."""
from __future__ import annotations

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.bot.states import AdminBalanceSG, AdminGrantCoinSG
from app.database.repositories import AdminLogsRepo, UsersRepo
from app.keyboards.admin import admin_back_kb
from app.locales import T
from app.security.sessions import AdminSessions
from app.services.coin_economy import CoinEconomy

router = Router(name="admin_balance")


def _guard(uid: int) -> bool:
    return AdminSessions.is_valid(uid)


async def _credit_and_notify(message_or_cb, admin_id: int, uid: int,
                             delta: float, bot: Bot) -> float:
    """Adjust balance, log, notify the user. Returns new balance."""
    new_balance = await CoinEconomy.adjust(
        uid, delta,
        reason="admin_grant" if delta > 0 else "admin_remove",
        related_id=str(admin_id),
    )
    await AdminLogsRepo.log(admin_id, "balance_adjust",
                            target_user=uid, payload=str(delta))
    try:
        if delta > 0:
            await bot.send_message(
                uid,
                T["user_balance_credited_notify"].format(
                    delta=delta, balance=round(new_balance, 2),
                ),
            )
    except Exception:
        pass
    return new_balance


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


# ───────────────────────── OBUNA → "Userga coin qo'shish" flow ─────────────

@router.callback_query(F.data == "adm:grant_coin_start")
async def grant_coin_start(cb: CallbackQuery, state: FSMContext) -> None:
    if not _guard(cb.from_user.id):
        await cb.answer(T["admin_session_expired"], show_alert=True)
        return
    await state.clear()
    await state.set_state(AdminGrantCoinSG.user_input)
    await cb.message.answer(T["admin_grant_coin_prompt"])
    await cb.answer()


@router.message(AdminGrantCoinSG.user_input, F.text)
async def grant_coin_user(message: Message, state: FSMContext) -> None:
    if not _guard(message.from_user.id):
        await state.clear()
        return
    q = (message.text or "").strip()
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
    await state.update_data(target_user_id=user["user_id"])
    await state.set_state(AdminGrantCoinSG.amount)
    await message.answer(T["admin_grant_coin_amount"].format(user_id=user["user_id"]))


@router.message(AdminGrantCoinSG.amount, F.text)
async def grant_coin_amount(message: Message, state: FSMContext, bot: Bot) -> None:
    if not _guard(message.from_user.id):
        await state.clear()
        return
    txt = (message.text or "").strip().replace(",", ".")
    try:
        delta = float(txt)
    except ValueError:
        await message.answer(T["admin_balance_bad_amount"])
        return
    data = await state.get_data()
    uid = data.get("target_user_id")
    await state.clear()
    if uid is None or not await UsersRepo.get(uid):
        await message.answer(T["admin_user_not_found"])
        return
    new_balance = await _credit_and_notify(message, message.from_user.id, uid, delta, bot)
    await message.answer(
        T["admin_balance_done"].format(
            user_id=uid, delta=delta, balance=round(new_balance, 2),
        ),
        reply_markup=admin_back_kb(),
    )


# ───────────────────────── /coin power command ─────────────────────────

@router.message(Command("coin"))
async def coin_command(message: Message, bot: Bot) -> None:
    if not _guard(message.from_user.id):
        await message.answer(T["admin_session_expired"])
        return
    parts = (message.text or "").split()
    if len(parts) != 3:
        await message.answer(T["admin_coin_usage"])
        return
    _, uid_str, amount_str = parts
    if not uid_str.lstrip("-").isdigit():
        await message.answer(T["admin_coin_usage"])
        return
    try:
        delta = float(amount_str.replace(",", "."))
    except ValueError:
        await message.answer(T["admin_coin_usage"])
        return
    uid = int(uid_str)
    if not await UsersRepo.get(uid):
        await message.answer(T["admin_user_not_found"])
        return
    new_balance = await _credit_and_notify(message, message.from_user.id, uid, delta, bot)
    await message.answer(
        T["admin_balance_done"].format(
            user_id=uid, delta=delta, balance=round(new_balance, 2),
        )
    )


def register(dp: Dispatcher) -> None:
    dp.include_router(router)
