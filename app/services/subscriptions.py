"""Subscription management."""
from __future__ import annotations

from datetime import datetime, timedelta

from app.database.repositories import SubscriptionsRepo, UsersRepo
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
    async def activate(user_id: int, plan: str, days: int = 30,
                       price: int = 0, payment_id: str | None = None) -> None:
        expires = (datetime.utcnow() + timedelta(days=days)).isoformat()
        await UsersRepo.set_plan(user_id, plan, expires)
        await SubscriptionsRepo.add(user_id, plan, price, expires, payment_id=payment_id)
        logger.info("subscription.activated",
                    extra={"user_id": user_id, "plan": plan, "expires": expires})

    @staticmethod
    async def start_purchase(user_id: int, plan: str) -> None:
        """Stub: log purchase intent. Real Click/Payme integration goes here."""
        logger.info("subscription.purchase_requested",
                    extra={"user_id": user_id, "plan": plan})
