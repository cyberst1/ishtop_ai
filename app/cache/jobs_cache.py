"""Aggregator-level cache (signed key prefix to avoid poisoning)."""
from __future__ import annotations

import hashlib

from app.cache.memory import TTLCache
from app.config import settings


class JobsCache:
    def __init__(self, ttl: float = 600.0):
        self._cache = TTLCache(ttl=ttl)

    def _safe_key(self, key: str) -> str:
        h = hashlib.sha256((settings.hmac_secret + ":" + key).encode()).hexdigest()[:24]
        return f"jobs:{h}"

    def get(self, key: str):
        return self._cache.get(self._safe_key(key))

    def set(self, key: str, value) -> None:
        self._cache.set(self._safe_key(key), value)
