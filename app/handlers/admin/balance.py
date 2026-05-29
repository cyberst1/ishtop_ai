"""Admin balance management — credit / debit any user."""
from __future__ import annotations

from aiogram import Dispatcher, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.bot.states import AdminBalanceSG
from app.database.repositories import AdminLogsRepo, UsersRepo
from app.locales import T
from app.security.sessions import AdminSessions
from app.services.coin_economy import CoinEconomy

router = Router(name="admin_balance")


@router.callback_query(F.data == "adm:balance")
async def open_balance(cb: CallbackQuery, state: FSMContext) -> None:
    if not AdminSessions.is_valid(cb.from_user.id):
        await cb.answer(T["admin_session_expired"], show_alert=True)
        return
    await state.set_state(AdminBalanceSG.user_id)
    await cb.message.answer("🪙 *Balans qo‘shish*\n\nUser ID kiriting:")
    await cb.answer()


@router.callback_query(F.data.startswith("adm:user:balance:"))
async def open_balance_for(cb: CallbackQuery, state: FSMContext) -> None:
    if not AdminSessions.is_valid(cb.from_user.id):
        await cb.answer(T["admin_session_expired"], show_alert=True)
        return
    uid = int(cb.data.split(":")[-1])
    await state.update_data(target_user_id=uid)
    await state.set_state(AdminBalanceSG.amount)
    await cb.message.answer(f"🪙 User `{uid}` uchun summa kiriting (manfiy = ayirish):")
    await cb.answer()


@router.message(AdminBalanceSG.user_id, F.text)
async def take_user_id(message: Message, state: FSMContext) -> None:
    if not AdminSessions.is_valid(message.from_user.id):
        return
    txt = (message.text or "").strip()
    if not txt.isdigit():
        await message.answer("❌ ID raqam bo‘lishi kerak.")
        return
    if not await UsersRepo.get(int(txt)):
        await message.answer("❌ User topilmadi.")
        return
    await state.update_data(target_user_id=int(txt))
    await state.set_state(AdminBalanceSG.amount)
    await message.answer("Summani kiriting (manfiy = ayirish):")


@router.message(AdminBalanceSG.amount, F.text)
async def take_amount(message: Message, state: FSMContext) -> None:
    if not AdminSessions.is_valid(message.from_user.id):
        return
    try:
        delta = float((message.text or "").replace(",", "."))
    except ValueError:
        await message.answer("❌ Noto‘g‘ri son.")
        return
    data = await state.get_data()
    uid = data["target_user_id"]
    bal = await CoinEconomy.adjust(uid, delta, reason="admin_grant" if delta > 0 else "admin_remove",
                                   related_id=str(message.from_user.id))
    await AdminLogsRepo.log(message.from_user.id, "balance_adjust",
                            target_user=uid, payload=str(delta))
    await state.clear()
    await message.answer(f"✅ Bajarildi. Yangi balans: *{round(bal, 2)}*")


def register(dp: Dispatcher) -> None:
    dp.include_router(router)
