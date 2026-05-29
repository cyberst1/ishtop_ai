"""Startup / shutdown hooks."""
from __future__ import annotations

from aiogram import Bot

from app.config import settings
from app.database.engine import get_db
from app.utils.logger import logger


async def on_startup(bot: Bot) -> None:
    db = get_db()
    await db.connect()
    await db.init_schema()
    me = await bot.get_me()
    logger.info("bot.started", extra={"username": me.username, "id": me.id, "mode": settings.mode})


async def on_shutdown(bot: Bot) -> None:
    await get_db().close()
    logger.info("bot.shutdown")
