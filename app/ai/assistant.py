"""ISH TOP AI — general-purpose AI assistant (chat + career)."""
from __future__ import annotations

from app.ai.client import AIClient
from app.ai.prompts import ISHTOP_AI_ASSISTANT
from app.config import settings
from app.locales import uz


class IshtopAI:
    @staticmethod
    async def answer(query: str) -> str:
        text = await AIClient.chat(ISHTOP_AI_ASSISTANT, query[:1500],
                                   temperature=0.6, max_tokens=900)
        if text:
            return text

        # No response — distinguish "not configured" vs "temporary failure"
        if not settings.effective_ai_api_key:
            return (
                "🤖 *ISH TOP AI hali to'liq yoqilmagan.*\n\n"
                "AI suhbat ishlashi uchun bot egasi OpenRouter API kalitini "
                "(`AI_API_KEY`) sozlashi kerak.\n\n"
                f"📩 Iltimos, admin bilan bog'laning: {uz.SUPPORT}"
            )
        return (
            "🤖 ISH TOP AI hozir javob bera olmadi (tarmoq yoki limit). "
            "Iltimos, 1-2 daqiqadan so'ng qayta urinib ko'ring."
        )
