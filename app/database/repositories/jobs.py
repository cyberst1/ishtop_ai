from __future__ import annotations

from typing import Iterable

from app.database.engine import get_db


class JobsRepo:
    @staticmethod
    async def upsert(job: dict) -> None:
        """job keys: id, source, title, company, location, salary, url, description, contact, is_remote, keywords"""
        db = get_db()
        await db.execute(
            """INSERT OR REPLACE INTO jobs
               (id, source, title, company, location, salary, url, description, contact,
                is_remote, keywords, ai_match_score, ai_scam_risk, ai_summary, fetched_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)""",
            (
                job["id"], job["source"], job["title"], job.get("company"),
                job.get("location"), job.get("salary"), job["url"],
                job.get("description"), job.get("contact"),
                int(bool(job.get("is_remote"))), job.get("keywords"),
                job.get("ai_match_score"), job.get("ai_scam_risk"), job.get("ai_summary"),
            ),
        )

    @staticmethod
    async def upsert_many(jobs: Iterable[dict]) -> int:
        n = 0
        for j in jobs:
            await JobsRepo.upsert(j)
            n += 1
        return n

    @staticmethod
    async def get(job_id: str):
        return await get_db().fetchone("SELECT * FROM jobs WHERE id = ?", (job_id,))

    @staticmethod
    async def save_for_user(user_id: int, job_id: str) -> None:
        await get_db().execute(
            "INSERT OR IGNORE INTO saved_jobs (user_id, job_id) VALUES (?, ?)",
            (user_id, job_id),
        )

    @staticmethod
    async def saved_count(user_id: int) -> int:
        row = await get_db().fetchone(
            "SELECT COUNT(*) AS c FROM saved_jobs WHERE user_id = ?", (user_id,)
        )
        return row["c"] if row else 0
