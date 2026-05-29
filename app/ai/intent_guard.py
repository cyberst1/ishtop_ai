"""
IntentGuard — first line of defense BEFORE any LLM call.
Saves cost and prevents off-topic abuse.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass

from app.ai.client import AIClient
from app.ai.prompts import INTENT_GUARD

# Cheap rules first — most cases never reach the LLM
_ALLOWED_KEYWORDS = {
    # english
    "job", "jobs", "work", "career", "salary", "interview", "resume", "cv",
    "hire", "hiring", "skill", "skills", "freelance", "freelancing", "roadmap",
    "remote", "office", "developer", "engineer", "manager", "designer", "marketing",
    "junior", "middle", "senior", "intern", "vacancy", "vakansiya",
    # uzbek + russian
    "ish", "ishchi", "xodim", "vakansi", "kasb", "karyera", "maosh", "intervyu",
    "rezyume", "rezume", "korikma", "ko'nikma", "yollanma", "ofis", "uydan",
    "rabota", "rabotnik", "vakansiya", "zarplata",
}

_BLOCKED_PATTERNS = [
    r"\b(hazil|jokes|sevg|love|siyosat|politics|prezident)\b",
    r"\b(she'r|poem|she\\'r)\b",
    r"\b(porno|sex|seks)\b",
]


@dataclass
class IntentVerdict:
    allowed: bool
    reason: str = ""


class IntentGuard:
    @staticmethod
    async def check(text: str) -> IntentVerdict:
        t = (text or "").lower().strip()
        if not t or len(t) > 500:
            return IntentVerdict(False, "empty_or_too_long")

        for pat in _BLOCKED_PATTERNS:
            if re.search(pat, t, flags=re.IGNORECASE):
                return IntentVerdict(False, "blocked_pattern")

        # Fast allow path: any career keyword present
        words = re.split(r"\W+", t)
        if any(w in _ALLOWED_KEYWORDS for w in words if w):
            return IntentVerdict(True)

        # Fallback: ask the LLM. If LLM unavailable, default to allow short queries.
        raw = await AIClient.chat(INTENT_GUARD, t, temperature=0.0, max_tokens=80)
        if not raw:
            return IntentVerdict(True)
        try:
            data = json.loads(raw)
            return IntentVerdict(bool(data.get("allowed", False)),
                                 str(data.get("reason", "")))
        except (ValueError, TypeError):
            return IntentVerdict(False, "parse_error")
