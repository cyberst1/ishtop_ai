"""Coin purchase requests — manual admin confirmation flow."""
from __future__ import annotations

from typing import Optional

import aiosqlite

from app.database.engine import get_db


class CoinPurchasesRepo:
    @staticmethod
    async def create(user_id: int, coins: int, price: int) -> int:
        """Create a pending purchase. Returns the new purchase id."""
        db = get_db()
        async with db.cursor() as cur:
            await cur.execute(
                """INSERT INTO coin_purchases (user_id, coins, price, status)
                   VALUES (?, ?, ?, 'pending')""",
                (user_id, coins, price),
            )
            return cur.lastrowid

    @staticmethod
    async def get(purchase_id: int) -> Optional[aiosqlite.Row]:
        return await get_db().fetchone(
            "SELECT * FROM coin_purchases WHERE id = ?", (purchase_id,)
        )

    @staticmethod
    async def list_pending(limit: int = 50) -> list[aiosqlite.Row]:
        return await get_db().fetchall(
            """SELECT cp.*, u.username, u.full_name
               FROM coin_purchases cp
               LEFT JOIN users u ON u.user_id = cp.user_id
               WHERE cp.status = 'pending'
               ORDER BY cp.created_at DESC
               LIMIT ?""",
            (limit,),
        )

    @staticmethod
    async def count_pending() -> int:
        row = await get_db().fetchone(
            "SELECT COUNT(*) AS c FROM coin_purchases WHERE status = 'pending'"
        )
        return row["c"] if row else 0

    @staticmethod
    async def list_recent(limit: int = 30) -> list[aiosqlite.Row]:
        return await get_db().fetchall(
            """SELECT cp.*, u.username, u.full_name
               FROM coin_purchases cp
               LEFT JOIN users u ON u.user_id = cp.user_id
               ORDER BY cp.created_at DESC
               LIMIT ?""",
            (limit,),
        )

    @staticmethod
    async def mark_confirmed(purchase_id: int, admin_id: int) -> None:
        await get_db().execute(
            """UPDATE coin_purchases
               SET status = 'confirmed', confirmed_by = ?, confirmed_at = CURRENT_TIMESTAMP
               WHERE id = ? AND status = 'pending'""",
            (admin_id, purchase_id),
        )

    @staticmethod
    async def mark_rejected(purchase_id: int, admin_id: int,
                            reason: str = "") -> None:
        await get_db().execute(
            """UPDATE coin_purchases
               SET status = 'rejected', confirmed_by = ?, confirmed_at = CURRENT_TIMESTAMP,
                   rejection_reason = ?
               WHERE id = ? AND status = 'pending'""",
            (admin_id, reason, purchase_id),
        )

    @staticmethod
    async def total_revenue() -> int:
        row = await get_db().fetchone(
            "SELECT COALESCE(SUM(price), 0) AS s FROM coin_purchases WHERE status = 'confirmed'"
        )
        return row["s"] if row else 0
