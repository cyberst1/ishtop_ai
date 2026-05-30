"""
/start — first-time vs returning user, optional referral payload.

  /start            → if new: create + 4 coin gift + welcome flow
                       if existing: short hello + main menu
  /start ref_<id>   → same as above, with referral attribution if new
"""
from __future__ import annotations

from aiogram import Dispatcher, F, Router
from aiogram.filters import CommandObject, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.config import settings
from app.database.repositories import UsersRepo
from app.keyboards import main_menu_kb
from app.locales import T
from app.services.referrals import ReferralService
from app.services.runtime_config import runtime
from app.services.subscriptions import SubscriptionService
from app.utils.logger import logger

router = Router(name="start")


def _parse_referrer(payload: str | None) -> int | None:
    if not payload or not payload.startswith("ref_"):
        return None
    try:
        return int(payload[4:])
    except (TypeError, ValueError):
        return None


@router.message(CommandStart(deep_link=True))
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext,
                    command: CommandObject | None = None) -> None:
    await state.clear()  # always clear FSM
    user = message.from_user
    if user is None:
        return

    existing = await UsersRepo.get(user.id)

    if existing is None:
        # First-time user — full welcome + 4 coin gift
        referrer_id = _parse_referrer(command.args if command else None)
        if referrer_id and (referrer_id == user.id or not await UsersRepo.get(referrer_id)):
            referrer_id = None

        await UsersRepo.create(
            user_id=user.id,
            username=user.username,
            full_name=user.full_name,
            referrer_id=referrer_id,
            signup_gift=runtime.signup_gift_coins,
        )
        if referrer_id:
            await ReferralService.reward(referrer_id, user.id)
        logger.info("user.signup", extra={"user_id": user.id, "referrer": referrer_id})

        is_pp = False
        await message.answer(T["start_welcome_new"], reply_markup=main_menu_kb(is_premium_plus=is_pp))
        return

    # Returning user — short hello + main menu
    await UsersRepo.upsert_seen(user.id, user.username, user.full_name)
    is_pp = await SubscriptionService.is_premium_plus(user.id)
    await message.answer(
        T["start_welcome_back"].format(name=user.first_name or "do'st"),
        reply_markup=main_menu_kb(is_premium_plus=is_pp),
    )


def register(dp: Dispatcher) -> None:
    dp.include_router(router)
