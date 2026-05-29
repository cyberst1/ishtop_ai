from aiogram import Dispatcher

from app.middlewares.antiflood import AntiFloodMiddleware
from app.middlewares.throttle import ThrottleMiddleware
from app.middlewares.ban_check import BanCheckMiddleware
from app.middlewares.logging_mw import LoggingMiddleware
from app.middlewares.i18n import I18nMiddleware


def register_all_middlewares(dp: Dispatcher) -> None:
    """Order matters: outer → inner."""
    dp.update.outer_middleware(LoggingMiddleware())
    dp.update.outer_middleware(BanCheckMiddleware())
    dp.message.middleware(AntiFloodMiddleware())
    dp.callback_query.middleware(AntiFloodMiddleware())
    dp.message.middleware(ThrottleMiddleware())
    dp.callback_query.middleware(ThrottleMiddleware())
    dp.message.middleware(I18nMiddleware())
    dp.callback_query.middleware(I18nMiddleware())


__all__ = ["register_all_middlewares"]
