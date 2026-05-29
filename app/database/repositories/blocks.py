from __future__ import annotations

from app.database.engine import get_db


class BlocksRepo:
    @staticmethod
    async def add(user_id: int, admin_id: int, action: str, reason: str | None) -> None:
        await get_db().execute(
            """INSERT INTO blocks (user_id, admin_id, action, reason)
               VALUES (?, ?, ?, ?)""",
            (user_id, admin_id, action, reason),
        )
