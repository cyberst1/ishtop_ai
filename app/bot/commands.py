"""
Telegram-native bot personalization:
  • Blue "/" command menu (set_my_commands)
  • Bot description (shown on the empty-chat splash before /start)
  • Short description (shown on the bot's profile page)

All text is Uzbek. Separate command sets are pushed for regular users and
for admins (admins additionally see /admin_kirish).
"""
from __future__ import annotations

from aiogram import Bot
from aiogram.types import (
    BotCommand,
    BotCommandScopeChat,
    BotCommandScopeDefault,
)

from app.config import settings
from app.utils.logger import logger

# ---- Public command menu (everyone) ----
USER_COMMANDS = [
    BotCommand(command="start",   description="🚀 Botni ishga tushirish"),
    BotCommand(command="search",  description="🔍 Ish qidirish"),
    BotCommand(command="profile", description="👤 Profilim va balans"),
    BotCommand(command="earn",    description="🪙 Coin ishlash"),
    BotCommand(command="plans",   description="⭐ Tariflar"),
    BotCommand(command="menu",    description="🏠 Bosh menyu"),
    BotCommand(command="help",    description="ℹ️ Yordam"),
    BotCommand(command="cancel",  description="❌ Bekor qilish"),
]

# ---- Admin gets the same + the secret entry ----
ADMIN_COMMANDS = USER_COMMANDS + [
    BotCommand(command="admin_kirish", description="🎛 Admin panel"),
]

BOT_DESCRIPTION = (
    "🤖 ISH TOP AI — O'zbekistondagi eng katta ish qidiruv yordamchisi.\n\n"
    "🔍 6 ta platformadan (OLX, HH.uz, Telegram kanallari va boshqalar) "
    "AI yordamida ish topib beradi.\n"
    "🧠 Tabiiy gap bilan yozsangiz ham tushunadi.\n"
    "📞 Bog'lanish ma'lumotlari bepul.\n\n"
    "Boshlash uchun «🚀 Ishga tushirish» yoki /start ni bosing."
)

BOT_SHORT_DESCRIPTION = (
    "🤖 AI yordamida O'zbekistondan ish toping. "
    "6 ta platforma, tabiiy qidiruv, bepul bog'lanish."
)


async def setup_bot_profile(bot: Bot) -> None:
    """Push commands + descriptions. Best-effort: never blocks startup."""
    # 1) Default commands for all users
    try:
        await bot.set_my_commands(USER_COMMANDS, scope=BotCommandScopeDefault())
    except Exception as e:
        logger.warning("commands.default_failed", extra={"err": str(e)[:160]})

    # 2) Admin-scoped commands
    for admin_id in settings.admin_ids:
        try:
            await bot.set_my_commands(
                ADMIN_COMMANDS, scope=BotCommandScopeChat(chat_id=admin_id)
            )
        except Exception as e:
            logger.warning("commands.admin_failed",
                           extra={"admin_id": admin_id, "err": str(e)[:160]})

    # 3) Descriptions (Uzbek). These show on the bot profile / empty chat.
    try:
        await bot.set_my_description(BOT_DESCRIPTION)
    except Exception as e:
        logger.warning("description_failed", extra={"err": str(e)[:160]})
    try:
        await bot.set_my_short_description(BOT_SHORT_DESCRIPTION)
    except Exception as e:
        logger.warning("short_description_failed", extra={"err": str(e)[:160]})

    logger.info("bot.profile_configured", extra={"commands": len(USER_COMMANDS)})
