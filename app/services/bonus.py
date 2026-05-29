"""Bonus-channel rewards: verify subscription via getChatMember → credit coins."""
from __future__ import annotations

from typing import Literal

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest

from app.database.repositories import BonusRepo
from app.services.coin_economy import CoinEconomy
from app.utils.logger import logger

ClaimResult = Literal["claimed", "not_subscribed", "rewarded", "error"]


class BonusService:
    @staticmethod
    async def claim(user_id: int, channel_id: int, bot: Bot) -> ClaimResult:
        if await BonusRepo.has_claimed(user_id, channel_id):
            return "claimed"
        # find channel
        rows = await BonusRepo.list_all()
        ch = next((r for r in rows if r["id"] == channel_id), None)
        if ch is None or not ch["enabled"]:
            return "error"
        # verify membership
        try:
            member = await bot.get_chat_member(ch["chat_id"], user_id)
            if member.status in ("left", "kicked"):
                return "not_subscribed"
        except TelegramBadRequest as e:
            logger.warning("bonus.check_failed", extra={"user_id": user_id, "err": str(e)})
            return "not_subscribed"
        # reward
        await CoinEconomy.credit(user_id, ch["reward"],
                                 reason="bonus_channel", related_id=str(channel_id))
        await BonusRepo.add_claim(user_id, channel_id, ch["reward"])
        return "rewarded"
