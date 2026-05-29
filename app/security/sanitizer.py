"""Input sanitization for user search queries / advisor prompts."""
from __future__ import annotations

import re

_CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_MAX_LEN = 200


def sanitize_query(text: str) -> str:
    if not text:
        return ""
    t = _CONTROL.sub("", text).strip()
    # remove leading slashes / @-mentions used to confuse routing
    t = re.sub(r"^[/@]+", "", t)
    # collapse whitespace
    t = re.sub(r"\s+", " ", t)
    if len(t) > _MAX_LEN:
        t = t[:_MAX_LEN]
    if len(t) < 2:
        return ""
    return t
