from __future__ import annotations

from typing import Optional

import aiosqlite

from app.database.engine import get_db


class UsersRepo:
    @staticmethod
    async def get(user_id: int) -> Optional[aiosqlite.Row]:
        return await get_db().fetchone("SELECT * FROM users WHERE user_id = ?", (user_id,))

    @staticmethod
    async def get_by_username(username: str) -> Optional[aiosqlite.Row]:
        return await get_db().fetchone(
            "SELECT * FROM users WHERE LOWER(username) = LOWER(?)", (username.lstrip("@"),)
        )

    @staticmethod
    async def create(user_id: int, username: str | None, full_name: str | None,
                     referrer_id: int | None = None, signup_gift: float = 0.0) -> None:
        db = get_db()
        async with db.cursor() as cur:
            await cur.execute(
                """INSERT INTO users (user_id, username, full_name, referrer_id, coin_balance)
                   VALUES (?, ?, ?, ?, ?)""",
                (user_id, username, full_name, referrer_id, signup_gift),
            )
            if signup_gift > 0:
                await cur.execute(
                    """INSERT INTO balances (user_id, delta, reason, balance_after)
                       VALUES (?, ?, 'signup_gift', ?)""",
                    (user_id, signup_gift, signup_gift),
                )

    @staticmethod
    async def upsert_seen(user_id: int, username: str | None, full_name: str | None) -> None:
        await get_db().execute(
            """UPDATE users SET username = ?, full_name = ?, last_seen_at = CURRENT_TIMESTAMP
               WHERE user_id = ?""",
            (username, full_name, user_id),
        )

    @staticmethod
    async def set_block(user_id: int, blocked: bool, reason: str | None = None) -> None:
        await get_db().execute(
            "UPDATE users SET is_blocked = ?, block_reason = ? WHERE user_id = ?",
            (1 if blocked else 0, reason, user_id),
        )

    @staticmethod
    async def is_blocked(user_id: int) -> bool:
        row = await get_db().fetchone(
            "SELECT is_blocked FROM users WHERE user_id = ?", (user_id,)
        )
        return bool(row and row["is_blocked"])

    @staticmethod
    async def set_plan(user_id: int, plan: str, expires_at: str | None) -> None:
        await get_db().execute(
            "UPDATE users SET plan = ?, plan_expires_at = ? WHERE user_id = ?",
            (plan, expires_at, user_id),
        )

    @staticmethod
    async def count_referrals(user_id: int) -> int:
        row = await get_db().fetchone(
            "SELECT COUNT(*) AS c FROM referrals WHERE referrer_id = ?", (user_id,)
        )
        return row["c"] if row else 0

    @staticmethod
    async def total_count() -> int:
        row = await get_db().fetchone("SELECT COUNT(*) AS c FROM users")
        return row["c"] if row else 0

    @staticmethod
    async def active_count(days: int = 7) -> int:
        row = await get_db().fetchone(
            f"SELECT COUNT(*) AS c FROM users WHERE last_seen_at > datetime('now', '-{int(days)} days')"
        )
        return row["c"] if row else 0

    @staticmethod
    async def list_paginated(offset: int = 0, limit: int = 20):
        return await get_db().fetchall(
            "SELECT * FROM users ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (limit, offset),
        )
