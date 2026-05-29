from __future__ import annotations

from app.database.engine import get_db


class AdminLogsRepo:
    @staticmethod
    async def log(admin_id: int, action: str, target_user: int | None = None,
                  payload: str | None = None, ip: str | None = None,
                  success: bool = True) -> None:
        await get_db().execute(
            """INSERT INTO admin_logs (admin_id, action, target_user, payload, ip, success)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (admin_id, action, target_user, payload, ip, 1 if success else 0),
        )

    @staticmethod
    async def recent(limit: int = 50):
        return await get_db().fetchall(
            "SELECT * FROM admin_logs ORDER BY created_at DESC LIMIT ?", (limit,)
        )
