"""
ISH TOP AI assistant service.

Access model:
  • Premium+        → unlimited AI chat
  • Everyone else   → FREE_AI_TRIAL (default 2) lifetime messages, then
                      must upgrade to Premium+.

General chat is allowed (no career-only IntentGuard here — that guard is
only for the job SEARCH flow). Every message is logged to ai_logs with
kind='assistant'.
"""
from __future__ import annotations

from app.ai.assistant import IshtopAI
from app.config import settings
from app.database.engine import get_db
from app.services.subscriptions import SubscriptionService

FREE_AI_TRIAL = 2  # lifetime free AI messages for non-Premium+ users


class AssistantService:
    @staticmethod
    async def usage_count(user_id: int) -> int:
        """Number of successful (non-blocked) assistant messages this user sent."""
        row = await get_db().fetchone(
            """SELECT COUNT(*) AS c FROM ai_logs
               WHERE user_id = ? AND kind = 'assistant' AND COALESCE(blocked, 0) = 0""",
            (user_id,),
        )
        return row["c"] if row else 0

    @staticmethod
    async def access(user_id: int) -> tuple[bool, str, int]:
        """
        Returns (allowed, reason, remaining_free).
          reason ∈ {"premium", "trial", "exhausted"}
          remaining_free is meaningful only for non-premium users.
        """
        if await SubscriptionService.is_premium_plus(user_id):
            return True, "premium", -1
        used = await AssistantService.usage_count(user_id)
        remaining = max(0, FREE_AI_TRIAL - used)
        if remaining > 0:
            return True, "trial", remaining
        return False, "exhausted", 0

    @staticmethod
    async def ask(user_id: int, query: str) -> str:
        """Generate an answer and log it. Caller must check access() first."""
        answer = await IshtopAI.answer(query)
        await get_db().execute(
            """INSERT INTO ai_logs (user_id, kind, prompt, response, blocked)
               VALUES (?, 'assistant', ?, ?, 0)""",
            (user_id, query[:1000], answer[:4000]),
        )
        return answer
