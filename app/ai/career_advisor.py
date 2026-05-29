"""Career roadmap & advice generator (Premium+ only)."""
from __future__ import annotations

from app.ai.client import AIClient
from app.ai.prompts import CAREER_ADVISOR


class CareerAdvisor:
    @staticmethod
    async def answer(query: str) -> str:
        text = await AIClient.chat(CAREER_ADVISOR, query[:1000],
                                   temperature=0.4, max_tokens=900)
        if not text:
            return ("🧠 Hozirda AI Career Advisor texnik sabablarga ko‘ra ishlamayapti. "
                    "Birozdan keyin urinib ko‘ring.")
        return text
