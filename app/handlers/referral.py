from __future__ import annotations

from aiogram import Dispatcher, F, Router
from aiogram.types import CallbackQuery

from app.config import settings
from app.database.repositories import UsersRepo
from app.locales import T

router = Router(name="referral")


def _ref_link(user_id: int) -> str:
    return f"https://t.me/{settings.bot_username}?start=ref_{user_id}"


@router.callback_query(F.data == "earn:invite")
@router.callback_query(F.data == "profile:invite")
async def show_invite(cb: CallbackQuery) -> None:
    count = await UsersRepo.count_referrals(cb.from_user.id)
    await cb.message.answer(
        T["invite_card"].format(link=_ref_link(cb.from_user.id), count=count)
    )
    await cb.answer()


def register(dp: Dispatcher) -> None:
    dp.include_router(router)
