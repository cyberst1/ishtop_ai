from __future__ import annotations

from app.database.engine import get_db


class ReferralsRepo:
    @staticmethod
    async def add(referrer_id: int, referred_id: int, coins: float) -> None:
        await get_db().execute(
            """INSERT OR IGNORE INTO referrals (referrer_id, referred_id, coins_awarded)
               VALUES (?, ?, ?)""",
            (referrer_id, referred_id, coins),
        )

    @staticmethod
    async def exists(referred_id: int) -> bool:
        row = await get_db().fetchone(
            "SELECT 1 FROM referrals WHERE referred_id = ?", (referred_id,)
        )
        return bool(row)

    @staticmethod
    async def total() -> int:
        row = await get_db().fetchone("SELECT COUNT(*) AS c FROM referrals")
        return row["c"] if row else 0
