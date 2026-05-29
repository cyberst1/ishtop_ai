"""Safe escape for Markdown (legacy v1 used by default ParseMode)."""
from __future__ import annotations

_SPECIALS = ("_", "*", "`", "[", "]")


def md_escape(text: object) -> str:
    s = "" if text is None else str(text)
    for ch in _SPECIALS:
        s = s.replace(ch, "\\" + ch)
    return s
