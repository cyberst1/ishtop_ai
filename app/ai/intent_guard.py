"""
IntentGuard — first line of defense BEFORE any LLM call or job search.
Saves cost and prevents off-topic abuse.

Verdict logic:
1. Empty / too long  →  reject
2. Matches a blocked pattern  →  reject (hazil, sevgi, siyosat, suhbat, ...)
3. Contains an allowed keyword (uz/ru/en) →  allow
4. Else: ask the LLM (only if NVIDIA_API_KEY is set)
5. Else (LLM unavailable): reject
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass

from app.ai.client import AIClient
from app.ai.prompts import INTENT_GUARD


# -------- Cheap rule-based filters (no API cost) --------

_ALLOWED_KEYWORDS = {
    # English
    "job", "jobs", "work", "career", "salary", "interview", "resume", "cv",
    "hire", "hiring", "skill", "skills", "freelance", "freelancing", "roadmap",
    "remote", "office", "developer", "engineer", "manager", "designer",
    "marketing", "junior", "middle", "senior", "intern", "vacancy",
    "programmer", "coder", "analyst", "tester", "qa", "devops", "data",
    "frontend", "backend", "fullstack", "mobile", "android", "ios",
    "python", "java", "javascript", "php", "ruby", "react", "angular", "vue",
    "node", "django", "fastapi", "flask", "spring", "rails",
    "sales", "smm", "seo", "hr", "accountant", "lawyer", "teacher",
    "driver", "courier", "cashier", "waiter", "cook", "chef",
    # Uzbek
    "ish", "ishchi", "xodim", "vakansi", "vakansiya", "kasb", "karyera",
    "maosh", "intervyu", "rezyume", "rezume", "konikma", "ko'nikma",
    "yollanma", "ofis", "uydan", "uyda", "masofadan",
    "dasturchi", "muhandis", "dizayner", "menejer", "marketolog",
    "sotuvchi", "savdo", "savdogar", "kuryer", "haydovchi",
    "oshpaz", "ofitsiant", "kassir", "buxgalter", "huquqshunos",
    "o'qituvchi", "tarbiyachi", "shifokor", "hamshira",
    "junior", "stajirovka", "amaliyot", "tajriba",
    "toshkent", "samarqand", "buxoro", "andijon", "namangan", "fargona",
    "navoi", "qarshi", "termiz", "nukus", "jizzax", "guliston",
    "tijorat", "biznes", "kompaniya", "korxona", "firma",
    # Russian
    "rabota", "rabotnik", "vakansiya", "zarplata", "stazhirovka",
    "programmist", "menedzher", "buxgalter", "voditel", "prodavec",
    "udalyon", "udalyonno", "ofis", "kompaniya",
}

_BLOCKED_PATTERNS = [
    r"\b(hazil|jokes?|kulgili|kulgu)\b",
    r"\b(sevgi|love|romantik|romance|qiz|kuyov)\b",
    r"\b(siyosat|politic|prezident|hukumat|deputat)\b",
    r"\b(she\W?r|poem|poems?|qoshiq|song|musiqa|music)\b",
    r"\b(porno|sex|seks|erotik|erotic|18\+)\b",
    r"\b(futbol|football|sport|kino|film|serial|movie)\b",
    r"\b(kasallik|disease|tibbiyot|tablet|dori|medication)\b",
    r"\b(dindor|namaz|prayer|cherkov|church|mecca)\b",
    r"\b(ovqat|food|retsept|recipe|tort|cake)\b",
    r"\b(salom|hello|hi|qalay|how are you|kayfingiz)\b",
    r"\b(ayt|aytib|gapir|suhbat|chat|chatla)\b.*",
    r"\bmenga\b.*\b(haqida|haqida)\b",
]

# At least 1 letter, at most 200 chars
_MIN_LEN = 2
_MAX_LEN = 200


@dataclass
class IntentVerdict:
    allowed: bool
    reason: str = ""


class IntentGuard:
    @staticmethod
    async def check(text: str) -> IntentVerdict:
        t = (text or "").lower().strip()
        if len(t) < _MIN_LEN or len(t) > _MAX_LEN:
            return IntentVerdict(False, "empty_or_too_long")

        # 1) Hard blocks
        for pat in _BLOCKED_PATTERNS:
            if re.search(pat, t, flags=re.IGNORECASE):
                return IntentVerdict(False, "blocked_pattern")

        # 2) Allowed-keyword fast path
        words = [w for w in re.split(r"\W+", t) if w]
        if any(w in _ALLOWED_KEYWORDS for w in words):
            return IntentVerdict(True)

        # 3) LLM fallback (only when API key present)
        raw = await AIClient.chat(INTENT_GUARD, t, temperature=0.0, max_tokens=80)
        if not raw:
            # No LLM available → strict default: reject
            return IntentVerdict(False, "no_career_keyword")
        try:
            data = json.loads(raw)
            return IntentVerdict(
                bool(data.get("allowed", False)),
                str(data.get("reason", "")),
            )
        except (ValueError, TypeError):
            return IntentVerdict(False, "parse_error")
