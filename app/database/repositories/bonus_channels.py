from __future__ import annotations

from app.database.engine import get_db


class BonusRepo:
    @staticmethod
    async def list_enabled():
        return await get_db().fetchall(
            "SELECT * FROM bonus_channels WHERE enabled = 1 ORDER BY id"
        )

    @staticmethod
    async def list_all():
        return await get_db().fetchall("SELECT * FROM bonus_channels ORDER BY id")

    @staticmethod
    async def add(chat_id: int, title: str, invite_link: str, reward: float = 0.5) -> None:
        await get_db().execute(
            """INSERT OR REPLACE INTO bonus_channels (chat_id, title, invite_link, reward, enabled)
               VALUES (?, ?, ?, ?, 1)""",
            (chat_id, title, invite_link, reward),
        )

    @staticmethod
    async def disable(channel_id: int) -> None:
        await get_db().execute(
            "UPDATE bonus_channels SET enabled = 0 WHERE id = ?", (channel_id,)
        )

    @staticmethod
    async def remove(channel_id: int) -> None:
        await get_db().execute("DELETE FROM bonus_channels WHERE id = ?", (channel_id,))

    @staticmethod
    async def has_claimed(user_id: int, channel_id: int) -> bool:
        row = await get_db().fetchone(
            "SELECT 1 FROM bonus_claims WHERE user_id = ? AND channel_id = ?",
            (user_id, channel_id),
        )
        return bool(row)

    @staticmethod
    async def add_claim(user_id: int, channel_id: int, coins: float) -> None:
        await get_db().execute(
            """INSERT OR IGNORE INTO bonus_claims (user_id, channel_id, coins)
               VALUES (?, ?, ?)""",
            (user_id, channel_id, coins),
        )
