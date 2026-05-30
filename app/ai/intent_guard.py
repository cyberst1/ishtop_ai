"""
IntentGuard — first line of defense BEFORE LLM / parsers.

Strategy is now BLOCK-LIST first (lenient by default):
  1. Empty / too-short / too-long           → reject
  2. Matches a known off-topic pattern      → reject
  3. Otherwise                              → allow

This lets users phrase their needs naturally in Uzbek/Russian/English,
e.g. "Telegram bot yasab beraman", "Web sayt qilib beraman", "Uyda ishlasam".

The LLM is only consulted when ambiguity remains (and a key is configured);
otherwise we trust the block-list and let the actual aggregator decide.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass

from app.ai.client import AIClient
from app.ai.prompts import INTENT_GUARD


# -------- Hard off-topic blocklist --------
# Conservative: matches must clearly NOT be career-related.
_BLOCKED_PATTERNS = [
    r"\bhazil\b|\bjokes?\b|\bkulgili\b",
    r"\bsevgi\b|\blove\b|\bromantik\b|\bromance\b",
    r"\bsiyosat\b|\bpolitics?\b|\bprezident\b|\bhukumat\b|\bdeputat\b",
    r"\bshe[' ]?r\b|\bpoems?\b|\bqo[' ]?shiq\b|\bsong\b|\bmusiqa\b|\bmusic\b",
    r"\bporno\b|\bsex\b|\bseks\b|\berotik\b|\b18\+\b",
    r"\bkasallik\b|\bdisease\b|\btablet\b|\bdori\b",
    r"\bnamaz\b|\bibodat\b|\bprayer\b|\bcherkov\b|\bchurch\b|\bmecca\b",
    r"\b(retsept|recipe)\b",
    # pure greeting only (allow if combined with topical word)
    r"^\s*(salom|hi|hello|qalaysiz|qalay|kayfingiz)[\s!?.,]*(salom|hi|hello|qalaysiz|qalay|kayfingiz)?[\s!?.,]*$",
    # explicit chat requests
    r"\b(suhbatlash|chatla|gaplash)\b",
    r"^\s*menga\s+(hazil|she[' ]?r|qo[' ]?shiq|hikoya)\s+ayt\b",
]

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

        # Hard off-topic blocks
        for pat in _BLOCKED_PATTERNS:
            if re.search(pat, t, flags=re.IGNORECASE):
                return IntentVerdict(False, f"blocked_pattern:{pat[:30]}")

        # Must contain at least one word with letters
        if not re.search(r"[a-zA-Zа-яёА-ЯЁ\u0400-\u04FF]{2,}", t):
            return IntentVerdict(False, "no_alpha_words")

        # Default: allow. The aggregator will simply return no results if
        # the query genuinely doesn't match any vacancy.
        return IntentVerdict(True)
