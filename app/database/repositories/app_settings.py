"""Runtime app-settings store — admin-editable key/value table."""
from __future__ import annotations

from typing import Optional

from app.database.engine import get_db


class AppSettingsRepo:
    @staticmethod
    async def get(key: str) -> Optional[str]:
        row = await get_db().fetchone(
            "SELECT value FROM app_settings WHERE key = ?", (key,)
        )
        return row["value"] if row else None

    @staticmethod
    async def set(key: str, value: str, admin_id: int | None = None) -> None:
        await get_db().execute(
            """INSERT INTO app_settings (key, value, updated_by)
                 VALUES (?, ?, ?)
               ON CONFLICT(key) DO UPDATE SET
                 value = excluded.value,
                 updated_at = CURRENT_TIMESTAMP,
                 updated_by = excluded.updated_by""",
            (key, value, admin_id),
        )

    @staticmethod
    async def all() -> dict[str, str]:
        rows = await get_db().fetchall("SELECT key, value FROM app_settings")
        return {r["key"]: r["value"] for r in rows}
