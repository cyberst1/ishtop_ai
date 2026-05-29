"""Token-bucket rate limiter (per key)."""
from __future__ import annotations

import time
from dataclasses import dataclass


@dataclass
class _Bucket:
    tokens: float
    last: float


class TokenBucket:
    def __init__(self, rate: float = 1.0, capacity: int = 5):
        """`rate` tokens per second, max `capacity` accumulated."""
        self.rate = rate
        self.capacity = capacity
        self._buckets: dict[object, _Bucket] = {}

    def allow(self, key: object, cost: float = 1.0) -> bool:
        now = time.monotonic()
        b = self._buckets.get(key)
        if b is None:
            b = _Bucket(tokens=float(self.capacity), last=now)
            self._buckets[key] = b
        # refill
        elapsed = now - b.last
        b.tokens = min(self.capacity, b.tokens + elapsed * self.rate)
        b.last = now
        if b.tokens >= cost:
            b.tokens -= cost
            return True
        return False
