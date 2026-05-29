from __future__ import annotations

from app.database.engine import get_db


class SearchesRepo:
    @staticmethod
    async def log(user_id: int, query: str, role: str | None,
                  parsed_keywords: str | None, results_count: int) -> None:
        await get_db().execute(
            """INSERT INTO searches (user_id, query, role, parsed_keywords, results_count)
               VALUES (?, ?, ?, ?, ?)""",
            (user_id, query, role, parsed_keywords, results_count),
        )

    @staticmethod
    async def count_today(user_id: int) -> int:
        row = await get_db().fetchone(
            """SELECT COUNT(*) AS c FROM searches
               WHERE user_id = ? AND date(created_at) = date('now')""",
            (user_id,),
        )
        return row["c"] if row else 0

    @staticmethod
    async def total() -> int:
        row = await get_db().fetchone("SELECT COUNT(*) AS c FROM searches")
        return row["c"] if row else 0
