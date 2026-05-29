"""/start with optional referral payload: /start ref_<user_id>"""
from __future__ import annotations

from aiogram import Dispatcher, F, Router
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message

from app.config import settings
from app.database.repositories import UsersRepo
from app.keyboards import main_menu_kb
from app.locales import T
from app.services.referrals import ReferralService
from app.utils.logger import logger

router = Router(name="start")


@router.message(CommandStart(deep_link=True))
@router.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject | None = None) -> None:
    user = message.from_user
    if user is None:
        return

    existing = await UsersRepo.get(user.id)
    referrer_id = None

    if existing is None:
        # Parse referral payload
        payload = command.args if command and command.args else None
        if payload and payload.startswith("ref_"):
            try:
                rid = int(payload[4:])
                if rid != user.id and await UsersRepo.get(rid):
                    referrer_id = rid
            except (ValueError, TypeError):
                pass

        await UsersRepo.create(
            user_id=user.id,
            username=user.username,
            full_name=user.full_name,
            referrer_id=referrer_id,
            signup_gift=settings.signup_gift_coins,
        )
        if referrer_id:
            await ReferralService.reward(referrer_id, user.id)
        logger.info("user.signup", extra={"user_id": user.id, "referrer": referrer_id})
    else:
        await UsersRepo.upsert_seen(user.id, user.username, user.full_name)

    is_pp = bool(existing and existing["plan"] == "premium_plus")
    await message.answer(T["start_welcome"], reply_markup=main_menu_kb(is_premium_plus=is_pp))


def register(dp: Dispatcher) -> None:
    dp.include_router(router)
