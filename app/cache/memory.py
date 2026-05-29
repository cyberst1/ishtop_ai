"""Tiny in-process TTL cache (thread-unsafe, asyncio-friendly)."""
from __future__ import annotations

import time
from typing import Any


class TTLCache:
    def __init__(self, ttl: float = 300.0, maxsize: int = 1024):
        self.ttl = ttl
        self.maxsize = maxsize
        self._store: dict[Any, tuple[float, Any]] = {}

    def get(self, key: Any) -> Any | None:
        rec = self._store.get(key)
        if rec is None:
            return None
        ts, val = rec
        if time.monotonic() - ts > self.ttl:
            self._store.pop(key, None)
            return None
        return val

    def set(self, key: Any, val: Any) -> None:
        if len(self._store) >= self.maxsize:
            # drop oldest 10%
            for k, _ in sorted(self._store.items(), key=lambda kv: kv[1][0])[: self.maxsize // 10 + 1]:
                self._store.pop(k, None)
        self._store[key] = (time.monotonic(), val)

    def delete(self, key: Any) -> None:
        self._store.pop(key, None)

    def clear(self) -> None:
        self._store.clear()
