from __future__ import annotations

from aiogram import Dispatcher, F, Router
from aiogram.types import Message

from app.database.repositories import JobsRepo, SearchesRepo, UsersRepo
from app.keyboards import profile_kb
from app.locales import T

router = Router(name="profile")

_PLAN_LABEL = {"free": T["plan_name_free"], "premium": T["plan_name_premium"],
                "premium_plus": T["plan_name_premium_plus"]}


@router.message(F.text == T["btn_profile"])
async def show_profile(message: Message) -> None:
    uid = message.from_user.id
    user = await UsersRepo.get(uid)
    if not user:
        await message.answer(T["error_generic"])
        return
    referrals = await UsersRepo.count_referrals(uid)
    saved = await JobsRepo.saved_count(uid)
    today = await SearchesRepo.count_today(uid)
    await message.answer(
        T["profile_card"].format(
            balance=round(user["coin_balance"], 2),
            plan=_PLAN_LABEL.get(user["plan"], user["plan"]),
            searches_today=today,
            referrals=referrals,
            saved=saved,
        ),
        reply_markup=profile_kb(),
    )


def register(dp: Dispatcher) -> None:
    dp.include_router(router)
