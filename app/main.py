"""ISH TOP AI — entrypoint."""
from __future__ import annotations

import asyncio

from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from app.bot import bot, dp
from app.bot.lifecycle import on_shutdown, on_startup
from app.config import settings
from app.handlers import register_all_handlers
from app.middlewares import register_all_middlewares
from app.utils.logger import logger


def build_app() -> None:
    register_all_middlewares(dp)
    register_all_handlers(dp)
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)


async def run_polling() -> None:
    build_app()
    logger.info("startup.mode", extra={"mode": "polling"})
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


async def run_webhook() -> None:
    build_app()
    app = web.Application()
    SimpleRequestHandler(
        dispatcher=dp, bot=bot, secret_token=settings.webhook_secret or None
    ).register(app, path="/webhook")
    setup_application(app, dp, bot=bot)
    await bot.set_webhook(
        settings.webhook_url,
        secret_token=settings.webhook_secret or None,
        allowed_updates=dp.resolve_used_update_types(),
    )
    logger.info("startup.mode", extra={"mode": "webhook", "url": settings.webhook_url})
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, settings.webapp_host, settings.webapp_port)
    await site.start()
    # keep running
    while True:
        await asyncio.sleep(3600)


async def main() -> None:
    if settings.mode == "webhook":
        await run_webhook()
    else:
        await run_polling()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("bot.exit")
