"""Startup / shutdown hooks."""
from __future__ import annotations

from aiogram import Bot

from app.bot.commands import setup_bot_profile
from app.config import settings
from app.database.engine import get_db
from app.services.runtime_config import runtime
from app.utils.logger import logger


async def on_startup(bot: Bot) -> None:
    db = get_db()
    await db.connect()
    await db.init_schema()
    await runtime.refresh()           # admin-editable settings from DB
    await setup_bot_profile(bot)      # blue / menu + descriptions
    me = await bot.get_me()
    logger.info(
        "bot.started",
        extra={"username": me.username, "id": me.id, "mode": settings.mode},
    )


async def on_shutdown(bot: Bot) -> None:
    try:
        await bot.session.close()
    except Exception:
        pass
    await get_db().close()
    logger.info("bot.shutdown")
