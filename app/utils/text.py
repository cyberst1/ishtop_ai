"""Text helpers."""
from __future__ import annotations


def truncate(text: str, n: int = 200, suffix: str = "…") -> str:
    if not text:
        return ""
    return text if len(text) <= n else text[: n - len(suffix)] + suffix


def clean_whitespace(text: str) -> str:
    return " ".join((text or "").split())
