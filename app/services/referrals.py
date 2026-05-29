"""Referral logic with multi-account / self-referral protection."""
from __future__ import annotations

from app.config import settings
from app.database.repositories import ReferralsRepo, UsersRepo
from app.security.abuse import AbuseDetector
from app.services.coin_economy import CoinEconomy
from app.utils.logger import logger


class ReferralService:
    @staticmethod
    async def reward(referrer_id: int, referred_id: int) -> bool:
        """Award coins to referrer for inviting `referred_id`. One-time per pair."""
        if referrer_id == referred_id:
            return False
        if await ReferralsRepo.exists(referred_id):
            return False
        # multi-account / abuse heuristic
        if await AbuseDetector.is_suspicious_referral(referrer_id, referred_id):
            logger.warning("referral.abuse", extra={"referrer": referrer_id, "referred": referred_id})
            return False

        prior = await UsersRepo.count_referrals(referrer_id)
        coins = settings.referral_first_bonus if prior == 0 else settings.referral_next_bonus
        await ReferralsRepo.add(referrer_id, referred_id, coins)
        await CoinEconomy.credit(referrer_id, coins, reason="referral",
                                 related_id=str(referred_id))
        logger.info("referral.rewarded",
                    extra={"referrer": referrer_id, "referred": referred_id, "coins": coins})
        return True
