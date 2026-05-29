from __future__ import annotations

from aiogram import Dispatcher, F, Router
from aiogram.types import CallbackQuery

from app.config import settings
from app.locales import T
from app.security.sessions import AdminSessions

router = Router(name="admin_settings")


@router.callback_query(F.data == "adm:settings")
async def show_settings(cb: CallbackQuery) -> None:
    if not AdminSessions.is_valid(cb.from_user.id):
        await cb.answer(T["admin_session_expired"], show_alert=True)
        return
    text = (
        "⚙️ *Sozlamalar*\n\n"
        f"• Mode: `{settings.mode}`\n"
        f"• Premium narx: `{settings.premium_price}` so‘m\n"
        f"• Premium+ narx: `{settings.premium_plus_price}` so‘m\n"
        f"• Free kunlik qidiruv: `{settings.free_daily_searches}`\n"
        f"• Job unlock narxi: `{settings.job_unlock_cost}` coin\n"
        f"• Signup sovg‘a: `{settings.signup_gift_coins}` coin\n"
        f"• Bonus kanal mukofoti: `{settings.bonus_channel_reward}` coin\n"
        f"• Parser timeout: `{settings.parser_timeout}` s\n"
        f"• Parser concurrency: `{settings.parser_concurrency}`"
    )
    await cb.message.edit_text(text)
    await cb.answer()


@router.callback_query(F.data == "adm:plans")
async def show_plans_admin(cb: CallbackQuery) -> None:
    if not AdminSessions.is_valid(cb.from_user.id):
        await cb.answer(T["admin_session_expired"], show_alert=True)
        return
    await cb.message.edit_text(
        "⭐ *Tariflar boshqaruvi*\n\n"
        "User kartasidan tarif berishingiz mumkin: `/find <id|@username>` → ⭐ Tarif berish."
    )
    await cb.answer()


def register(dp: Dispatcher) -> None:
    dp.include_router(router)
