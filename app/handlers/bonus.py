from __future__ import annotations

from aiogram import Dispatcher, F, Router
from aiogram.types import CallbackQuery, Message

from app.database.repositories import BonusRepo
from app.keyboards import bonus_channels_kb, earn_kb
from app.locales import T
from app.services.bonus import BonusService

router = Router(name="bonus")


@router.message(F.text == T["btn_earn"])
async def show_earn(message: Message) -> None:
    await message.answer(T["earn_header"], reply_markup=earn_kb())


@router.callback_query(F.data == "earn:bonus")
async def show_bonus_channels(cb: CallbackQuery) -> None:
    channels = await BonusRepo.list_enabled()
    if not channels:
        await cb.message.answer(T["bonus_no_channels"])
        await cb.answer()
        return
    await cb.message.answer(T["bonus_channels_header"],
                            reply_markup=bonus_channels_kb([dict(c) for c in channels]))
    await cb.answer()


@router.callback_query(F.data.startswith("bonus:check:"))
async def check_membership(cb: CallbackQuery) -> None:
    channel_id = int(cb.data.split(":", 2)[2])
    result = await BonusService.claim(cb.from_user.id, channel_id, cb.bot)
    if result == "claimed":
        await cb.answer(T["bonus_already_claimed"], show_alert=True)
    elif result == "not_subscribed":
        await cb.answer(T["bonus_not_subscribed"], show_alert=True)
    elif result == "rewarded":
        await cb.answer(T["bonus_rewarded"], show_alert=True)
    else:
        await cb.answer(T["error_generic"], show_alert=True)


def register(dp: Dispatcher) -> None:
    dp.include_router(router)
