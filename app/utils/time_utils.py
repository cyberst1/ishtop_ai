"""Time helpers."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def in_days(days: int) -> datetime:
    return utcnow() + timedelta(days=days)


def is_expired(iso_ts: str | None) -> bool:
    if not iso_ts:
        return False
    try:
        return datetime.fromisoformat(iso_ts) < datetime.utcnow()
    except (TypeError, ValueError):
        return False
