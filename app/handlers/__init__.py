from aiogram import Dispatcher

from app.handlers import (
    start, search, profile, plans, bonus, referral, help as help_h, advisor,
    coins,
)
from app.handlers.admin import (
    login as admin_login,
    users as admin_users,
    blocks as admin_blocks,
    balance as admin_balance,
    broadcast as admin_broadcast,
    bonus_channels as admin_bonus,
    stats as admin_stats,
    settings as admin_settings,
    security as admin_security,
    payments as admin_payments,
)


def register_all_handlers(dp: Dispatcher) -> None:
    # Admin first (specific commands like /admin_kirish)
    admin_login.register(dp)
    admin_users.register(dp)
    admin_blocks.register(dp)
    admin_balance.register(dp)
    admin_broadcast.register(dp)
    admin_bonus.register(dp)
    admin_stats.register(dp)
    admin_settings.register(dp)
    admin_security.register(dp)
    admin_payments.register(dp)

    # User handlers
    start.register(dp)
    search.register(dp)
    profile.register(dp)
    plans.register(dp)
    bonus.register(dp)
    referral.register(dp)
    help_h.register(dp)
    advisor.register(dp)
    coins.register(dp)


__all__ = ["register_all_handlers"]
