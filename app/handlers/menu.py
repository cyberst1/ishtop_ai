"""
Universal navigation commands available everywhere:

  /menu    — clear FSM and show the main menu
  /cancel  — alias of /menu (used to exit any flow)

These bypass FSM filters so users can always escape a stuck state.
"""
from __future__ import annotations

from aiogram import Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.database.repositories import UsersRepo
from app.keyboards import main_menu_kb
from app.locales import T
from app.services.subscriptions import SubscriptionService

router = Router(name="menu")


async def _show_main_menu(message: Message, *, with_text: bool = True) -> None:
    user_id = message.from_user.id
    is_pp = await SubscriptionService.is_premium_plus(user_id)
    if with_text:
        await message.answer(T["main_menu_text"], reply_markup=main_menu_kb(is_premium_plus=is_pp))
    else:
        await message.answer("🏠", reply_markup=main_menu_kb(is_premium_plus=is_pp))


@router.message(Command("menu"))
async def cmd_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    await UsersRepo.upsert_seen(
        message.from_user.id, message.from_user.username, message.from_user.full_name
    )
    await _show_main_menu(message)


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    cur = await state.get_state()
    await state.clear()
    if cur:
        await message.answer(T["cancel_done"])
    await _show_main_menu(message, with_text=False)


def register(dp: Dispatcher) -> None:
    dp.include_router(router)
