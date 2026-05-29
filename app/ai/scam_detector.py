"""Heuristic + LLM scam-risk scoring."""
from __future__ import annotations

import json
import re

from app.ai.client import AIClient
from app.ai.prompts import SCAM_DETECTOR

_SCAM_FLAGS = [
    r"oson pul", r"easy money", r"100% kafolat",
    r"depozit", r"deposit", r"investitsiya", r"investment",
    r"telegram\s*bot.*?ish\s*ber",
    r"\b(million|mln)\s*so'?m.*?(uy|home)\b",
]


class ScamDetector:
    @staticmethod
    async def score(text: str) -> tuple[int, str]:
        text = (text or "")[:4000]
        flags = sum(1 for p in _SCAM_FLAGS if re.search(p, text, flags=re.IGNORECASE))
        baseline = min(100, flags * 25)

        raw = await AIClient.chat(SCAM_DETECTOR, text, temperature=0.0, max_tokens=120)
        if not raw:
            return baseline, "rule-based"
        try:
            data = json.loads(raw)
            risk = int(data.get("risk", baseline))
            reason = str(data.get("reason", ""))
            return max(0, min(100, risk)), reason
        except (ValueError, TypeError):
            return baseline, "rule-based"
