from __future__ import annotations

from app.database.engine import get_db


class SubscriptionsRepo:
    @staticmethod
    async def add(user_id: int, plan: str, price: int, expires_at: str,
                  payment_provider: str | None = None, payment_id: str | None = None) -> None:
        await get_db().execute(
            """INSERT INTO subscriptions
               (user_id, plan, price, expires_at, payment_provider, payment_id)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, plan, price, expires_at, payment_provider, payment_id),
        )

    @staticmethod
    async def count_premium() -> int:
        row = await get_db().fetchone(
            """SELECT COUNT(DISTINCT user_id) AS c FROM users
               WHERE plan IN ('premium','premium_plus')
                 AND (plan_expires_at IS NULL OR plan_expires_at > datetime('now'))"""
        )
        return row["c"] if row else 0
