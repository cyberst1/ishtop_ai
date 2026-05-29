"""AI Career Advisor — Premium+ only, intent-guarded."""
from __future__ import annotations

from app.ai.career_advisor import CareerAdvisor
from app.ai.intent_guard import IntentGuard
from app.database.engine import get_db
from app.locales import T


class AdvisorService:
    @staticmethod
    async def ask(user_id: int, query: str) -> str:
        verdict = await IntentGuard.check(query)
        if not verdict.allowed:
            await get_db().execute(
                """INSERT INTO ai_logs (user_id, kind, prompt, blocked) VALUES (?, 'advisor', ?, 1)""",
                (user_id, query[:1000]),
            )
            return T["search_off_topic"]

        answer = await CareerAdvisor.answer(query)
        await get_db().execute(
            """INSERT INTO ai_logs (user_id, kind, prompt, response) VALUES (?, 'advisor', ?, ?)""",
            (user_id, query[:1000], answer[:4000]),
        )
        return answer
