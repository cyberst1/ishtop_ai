"""In-process admin session store. Idle TTL = settings.admin_session_ttl_minutes."""
from __future__ import annotations

import time

from app.config import settings


class AdminSessions:
    _store: dict[int, float] = {}  # admin_id -> expires_at (monotonic)

    @classmethod
    def create(cls, admin_id: int) -> None:
        cls._store[admin_id] = time.monotonic() + settings.admin_session_ttl_minutes * 60

    @classmethod
    def is_valid(cls, admin_id: int) -> bool:
        if admin_id not in settings.admin_ids:
            return False
        exp = cls._store.get(admin_id)
        if exp is None or time.monotonic() > exp:
            cls._store.pop(admin_id, None)
            return False
        # refresh on activity
        cls._store[admin_id] = time.monotonic() + settings.admin_session_ttl_minutes * 60
        return True

    @classmethod
    def revoke(cls, admin_id: int) -> None:
        cls._store.pop(admin_id, None)
