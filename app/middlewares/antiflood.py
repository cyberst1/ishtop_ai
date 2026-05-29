"""Sliding-window anti-flood: max N events per W seconds per user."""
from __future__ import annotations

import time
from collections import defaultdict, deque
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from app.config import settings
from app.locales import T


class AntiFloodMiddleware(BaseMiddleware):
    def __init__(self, window: float = 60.0, max_events: int | None = None):
        self.window = window
        self.max_events = max_events or settings.rate_limit_per_min
        self._buckets: Dict[int, deque[float]] = defaultdict(deque)
        self._notified: Dict[int, float] = {}

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        if user is None:
            return await handler(event, data)

        now = time.monotonic()
        bucket = self._buckets[user.id]

        while bucket and now - bucket[0] > self.window:
            bucket.popleft()

        if len(bucket) >= self.max_events:
            # send "rate limited" once every window
            if now - self._notified.get(user.id, 0) > 5:
                self._notified[user.id] = now
                try:
                    if isinstance(event, Message):
                        await event.answer(T["rate_limited"])
                    elif isinstance(event, CallbackQuery):
                        await event.answer(T["rate_limited"], show_alert=False)
                except Exception:
                    pass
            return

        bucket.append(now)
        return await handler(event, data)
