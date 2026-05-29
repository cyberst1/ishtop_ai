"""Structured logging + global error handler."""
from __future__ import annotations

import time
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject, Update

from app.locales import T
from app.utils.logger import logger


class LoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        start = time.monotonic()
        try:
            result = await handler(event, data)
            elapsed = (time.monotonic() - start) * 1000
            logger.info(
                "update.handled",
                extra={
                    "user_id": getattr(user, "id", None),
                    "elapsed_ms": round(elapsed, 1),
                    "type": type(event).__name__,
                },
            )
            return result
        except Exception as e:
            logger.exception("update.error", extra={"user_id": getattr(user, "id", None)})
            inner = None
            if isinstance(event, Update):
                inner = event.message or event.callback_query
            elif isinstance(event, (Message, CallbackQuery)):
                inner = event
            try:
                if isinstance(inner, Message):
                    await inner.answer(T["error_generic"])
                elif isinstance(inner, CallbackQuery):
                    await inner.answer(T["error_generic"], show_alert=True)
            except Exception:
                pass
            return None
