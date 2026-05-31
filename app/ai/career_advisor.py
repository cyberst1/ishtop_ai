"""Career roadmap & advice generator (Premium+ only)."""
from __future__ import annotations

from app.ai.client import AIClient
from app.ai.prompts import CAREER_ADVISOR
from app.config import settings
from app.locales import uz


class CareerAdvisor:
    @staticmethod
    async def answer(query: str) -> str:
        text = await AIClient.chat(CAREER_ADVISOR, query[:1000],
                                   temperature=0.4, max_tokens=900)
        if text:
            return text

        # No response — distinguish "not configured" vs "temporary failure"
        if not settings.effective_ai_api_key:
            return (
                "🧠 *AI Career Advisor hali yoqilmagan.*\n\n"
                "Bu funksiya ishlashi uchun bot egasi OpenRouter API kalitini "
                "(`AI_API_KEY`) sozlashi kerak.\n\n"
                f"📩 Iltimos, admin bilan bog'laning: {uz.SUPPORT}"
            )
        return (
            "🧠 AI Career Advisor hozir javob bera olmadi (tarmoq yoki limit). "
            "Iltimos, 1-2 daqiqadan so'ng qayta urinib ko'ring."
        )

