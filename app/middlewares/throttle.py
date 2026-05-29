"""Per-action cooldowns (search: 5s, AI: 10s, generic: 0.5s)."""
from __future__ import annotations

import time
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

ACTION_COOLDOWNS = {
    "search": 5.0,
    "ai": 10.0,
    "default": 0.4,
}


class ThrottleMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        self._last: Dict[tuple[int, str], float] = {}

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        if user is None:
            return await handler(event, data)

        action = "default"
        if isinstance(event, Message) and event.text:
            t = event.text.lower()
            if "qidir" in t or "search" in t:
                action = "search"
        elif isinstance(event, CallbackQuery) and event.data:
            if event.data.startswith("search:") or event.data == "search":
                action = "search"
            elif event.data.startswith("ai:") or event.data == "advisor":
                action = "ai"

        cd = ACTION_COOLDOWNS.get(action, ACTION_COOLDOWNS["default"])
        now = time.monotonic()
        key = (user.id, action)
        last = self._last.get(key, 0)
        if now - last < cd:
            if isinstance(event, CallbackQuery):
                try:
                    await event.answer("⏳", show_alert=False)
                except Exception:
                    pass
            return
        self._last[key] = now
        return await handler(event, data)
