"""Subscription management."""
from __future__ import annotations

from datetime import datetime, timedelta

from app.database.repositories import SubscriptionsRepo, UsersRepo
from app.services.coin_economy import CoinEconomy
from app.services.runtime_config import runtime
from app.utils.logger import logger


class SubscriptionService:
    @staticmethod
    async def is_premium(user_id: int) -> bool:
        u = await UsersRepo.get(user_id)
        if not u:
            return False
        if u["plan"] not in ("premium", "premium_plus"):
            return False
        if u["plan_expires_at"] is None:
            return True
        try:
            return datetime.fromisoformat(u["plan_expires_at"]) > datetime.utcnow()
        except (TypeError, ValueError):
            return True

    @staticmethod
    async def is_premium_plus(user_id: int) -> bool:
        u = await UsersRepo.get(user_id)
        if not u or u["plan"] != "premium_plus":
            return False
        if u["plan_expires_at"] is None:
            return True
        try:
            return datetime.fromisoformat(u["plan_expires_at"]) > datetime.utcnow()
        except (TypeError, ValueError):
            return True

    @staticmethod
    async def activate(user_id: int, plan: str, days: int | None = None,
                       price: int = 0, payment_id: str | None = None) -> float:
        """
        Activate a plan. Returns the number of bonus coins granted (0 for none).

        • Duration defaults to runtime.plan_duration_days (14) for paid plans.
        • Premium+ grants runtime.premium_plus_bonus_coins (30) bonus coins.
        • 'free' is effectively unlimited duration.
        """
        if days is None:
            days = 365 * 10 if plan == "free" else int(runtime.plan_duration_days)

        expires = (datetime.utcnow() + timedelta(days=days)).isoformat()
        await UsersRepo.set_plan(user_id, plan, expires)
        await SubscriptionsRepo.add(user_id, plan, price, expires, payment_id=payment_id)

        bonus = 0.0
        if plan == "premium_plus":
            bonus = float(runtime.premium_plus_bonus_coins or 0)
            if bonus > 0:
                await CoinEconomy.credit(user_id, bonus, reason="plan_bonus",
                                         related_id=plan)

        logger.info("subscription.activated",
                    extra={"user_id": user_id, "plan": plan,
                           "expires": expires, "bonus": bonus})
        return bonus

    @staticmethod
    async def start_purchase(user_id: int, plan: str) -> None:
        """Stub: log purchase intent. Real Click/Payme integration goes here."""
        logger.info("subscription.purchase_requested",
                    extra={"user_id": user_id, "plan": plan})
