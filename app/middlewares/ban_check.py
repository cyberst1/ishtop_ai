"""Reject all events from blocked users (except admins)."""
from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject, Update

from app.config import settings
from app.database.repositories import UsersRepo
from app.locales import T


class BanCheckMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        if user is None or user.id in settings.admin_ids:
            return await handler(event, data)

        if await UsersRepo.is_blocked(user.id):
            inner = None
            if isinstance(event, Update):
                inner = event.message or event.callback_query
            elif isinstance(event, (Message, CallbackQuery)):
                inner = event
            try:
                if isinstance(inner, Message):
                    await inner.answer(T["blocked"])
                elif isinstance(inner, CallbackQuery):
                    await inner.answer(T["blocked"], show_alert=True)
            except Exception:
                pass
            return
        return await handler(event, data)
