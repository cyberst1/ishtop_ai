"""
IntentGuard — gate-keeper that runs before parsers / LLM analyzer.

Three-tier strategy:

  1. HARD BLOCK list  — obvious off-topic patterns (hazil, sevgi, ...) → REJECT
  2. STRONG ALLOW list — known career keyword present                 → ALLOW
  3. LLM ARBITER       — ambiguous query is sent to the LLM. If LLM says
                          allowed=true → ALLOW. Otherwise (or LLM
                          unavailable) → REJECT (strict default).

Keeps natural Uzbek phrasing working ("Telegram bot yasab beraman") AND
rejects anything off-topic ("iPhone 15 sotib olaman", "kitob tavsiya qil").
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass

from app.ai.client import AIClient
from app.ai.prompts import INTENT_GUARD
from app.ai.job_analyzer import _SYNONYMS  # reuse the canonical lexicon


# ---- Hard off-topic blocks ----------------------------------------------

_BLOCKED_PATTERNS = [
    r"\bhazil\b|\bjokes?\b|\bkulgili\b",
    r"\bsevgi\b|\blove\b|\bromantik\b|\bromance\b",
    r"\bsiyosat\b|\bpolitics?\b|\bprezident\b|\bhukumat\b|\bdeputat\b",
    r"\bshe[' ]?r\b|\bpoems?\b|\bqo[' ]?shiq\b|\bsong\b|\bmusiqa\b|\bmusic\b",
    r"\bporno\b|\bsex\b|\bseks\b|\berotik\b|\b18\+\b",
    r"\bkasallik\b|\bdisease\b|\btablet\b|\bdori\b|\btibbiyot\b",
    r"\bnamaz\b|\bibodat\b|\bprayer\b|\bcherkov\b|\bchurch\b|\bmecca\b|\bdin\b",
    r"\b(retsept|recipe)\b",
    r"^\s*(salom|hi|hello|qalaysiz|qalay|kayfingiz)[\s!?.,]*"
        r"(salom|hi|hello|qalaysiz|qalay|kayfingiz)?[\s!?.,]*$",
    r"\b(suhbatlash|chatla|gaplash)\b",
    r"^\s*menga\s+(hazil|she[' ]?r|qo[' ]?shiq|hikoya)\s+ayt\b",
    # explicit purchases (not job-related)
    r"\b(sotib\s+ol(am(an|aymiz)|in)|buy\b|kupit)\b.*\b(iphone|phone|telefon|kitob|book|kompyuter|laptop|mashina|car|televizor|televizion|smartfon)\b",
    # generic curiosity
    r"\b(nima\s+bu|what\s+is|haqida\s+ayt|tavsiya\s+qil|recommend)\b",
    r"\b(qancha|narxi|cost|price)\b.*\b(iphone|telefon|mashina|kitob)\b",
    r"\b(bitcoin|kripto|crypto|nft)\b",
]

# ---- Strong allow keywords (instant-allow) ----
# Combine the JobAnalyzer synonym table with explicit English/Uzbek vocab.
# Words mapped to "" (ignore) in synonyms must NOT short-circuit allow.
_BASE_ALLOW = {
    # English
    "job", "jobs", "work", "career", "salary", "interview", "resume", "cv",
    "hire", "hiring", "skill", "skills", "freelance", "freelancing", "roadmap",
    "remote", "office", "developer", "engineer", "manager", "designer",
    "marketing", "junior", "middle", "senior", "intern", "vacancy",
    "programmer", "coder", "analyst", "tester", "qa", "devops",
    "frontend", "backend", "fullstack", "mobile", "android", "ios",
    "python", "java", "javascript", "php", "react", "node", "django",
    "fastapi", "flask", "spring",
    "sales", "smm", "seo", "hr", "accountant", "lawyer", "teacher",
    "driver", "courier", "cashier", "waiter", "cook", "chef",
    # Uzbek/Russian
    "ish", "ishchi", "xodim", "vakansi", "vakansiya", "kasb", "karyera",
    "maosh", "intervyu", "rezyume", "yollanma", "ofis", "uydan", "uyda",
    "masofadan", "rabota", "rabotnik", "zarplata", "stazhirovka", "amaliyot",
}
_ALLOWED_KEYWORDS = (
    _BASE_ALLOW
    | {k for k, v in _SYNONYMS.items() if v}  # any synonym mapped to non-empty
)

_MIN_LEN = 2
_MAX_LEN = 300


@dataclass
class IntentVerdict:
    allowed: bool
    reason: str = ""


class IntentGuard:
    @staticmethod
    async def check(text: str) -> IntentVerdict:
        t = (text or "").lower().strip()
        if len(t) < _MIN_LEN:
            return IntentVerdict(False, "empty")
        if len(t) > _MAX_LEN:
            return IntentVerdict(False, "too_long")

        # 1) Hard blocks
        for pat in _BLOCKED_PATTERNS:
            if re.search(pat, t, flags=re.IGNORECASE):
                return IntentVerdict(False, "blocked_pattern")

        # 2) Quick allow (career keyword present)
        words = [w for w in re.split(r"[^\wʻ']+", t) if w]
        # Strip Uzbek case suffixes for keyword check
        from app.ai.job_analyzer import _stem
        for w in words:
            if w in _ALLOWED_KEYWORDS or _stem(w) in _ALLOWED_KEYWORDS:
                return IntentVerdict(True, "keyword_match")

        # 3) LLM arbiter (strict — uncertain → reject)
        raw = await AIClient.chat(INTENT_GUARD, t, temperature=0.0, max_tokens=120)
        if not raw:
            return IntentVerdict(False, "no_career_keyword_no_llm")
        try:
            data = json.loads(_extract_json(raw))
            allowed = bool(data.get("allowed", False))
            reason = str(data.get("reason", ""))
            return IntentVerdict(allowed, reason or "llm_decision")
        except (ValueError, TypeError):
            return IntentVerdict(False, "parse_error")


def _extract_json(text: str) -> str:
    """Some models wrap JSON in ```...``` fences — strip them."""
    text = text.strip()
    # Remove markdown code fence
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```\s*$", "", text)
    return text.strip()
