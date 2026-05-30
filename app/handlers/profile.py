"""User profile: balance, plan, today's stats, saved jobs link."""
from __future__ import annotations

from aiogram import Dispatcher, F, Router
from aiogram.types import CallbackQuery, Message

from app.database.repositories import JobsRepo, SearchesRepo, UsersRepo
from app.keyboards import profile_kb
from app.locales import T

router = Router(name="profile")

_PLAN_LABEL = {"free": "Free", "premium": "Premium", "premium_plus": "Premium+"}


async def _send_profile_card(target) -> None:
    user_id = target.from_user.id
    user = await UsersRepo.get(user_id)
    if not user:
        msg = T["error_generic"]
        if isinstance(target, Message):
            await target.answer(msg)
        else:
            await target.message.answer(msg)
        return

    referrals = await UsersRepo.count_referrals(user_id)
    saved = await JobsRepo.saved_count(user_id)
    today = await SearchesRepo.count_today(user_id)
    text = T["profile_card"].format(
        balance=round(user["coin_balance"], 2),
        plan=_PLAN_LABEL.get(user["plan"], user["plan"]),
        searches_today=today,
        referrals=referrals,
        saved=saved,
    )
    if isinstance(target, Message):
        await target.answer(text, reply_markup=profile_kb(saved_count=saved))
    else:
        try:
            await target.message.edit_text(text, reply_markup=profile_kb(saved_count=saved))
        except Exception:
            await target.message.answer(text, reply_markup=profile_kb(saved_count=saved))


@router.message(F.text == T["btn_profile"])
async def show_profile(message: Message) -> None:
    await _send_profile_card(message)


@router.callback_query(F.data == "profile:home")
async def back_to_profile(cb: CallbackQuery) -> None:
    await _send_profile_card(cb)
    await cb.answer()


def register(dp: Dispatcher) -> None:
    dp.include_router(router)
