from __future__ import annotations

from aiogram import Dispatcher, F, Router
from aiogram.types import CallbackQuery

from app.database.repositories import AdminLogsRepo, BlocksRepo, UsersRepo
from app.locales import T
from app.security.sessions import AdminSessions

router = Router(name="admin_blocks")


@router.callback_query(F.data.startswith("adm:user:block:"))
async def block_user(cb: CallbackQuery) -> None:
    if not AdminSessions.is_valid(cb.from_user.id):
        await cb.answer(T["admin_session_expired"], show_alert=True)
        return
    uid = int(cb.data.split(":")[-1])
    await UsersRepo.set_block(uid, True, "admin_block")
    await BlocksRepo.add(uid, cb.from_user.id, "block", "admin_block")
    await AdminLogsRepo.log(cb.from_user.id, "block", target_user=uid)
    await cb.answer("🚫 Bloklandi.", show_alert=True)


@router.callback_query(F.data.startswith("adm:user:unblock:"))
async def unblock_user(cb: CallbackQuery) -> None:
    if not AdminSessions.is_valid(cb.from_user.id):
        await cb.answer(T["admin_session_expired"], show_alert=True)
        return
    uid = int(cb.data.split(":")[-1])
    await UsersRepo.set_block(uid, False, None)
    await BlocksRepo.add(uid, cb.from_user.id, "unblock", None)
    await AdminLogsRepo.log(cb.from_user.id, "unblock", target_user=uid)
    await cb.answer("✅ Blokdan chiqarildi.", show_alert=True)


@router.callback_query(F.data == "adm:blocks")
async def show_blocks_panel(cb: CallbackQuery) -> None:
    if not AdminSessions.is_valid(cb.from_user.id):
        await cb.answer(T["admin_session_expired"], show_alert=True)
        return
    await cb.message.edit_text(
        "🚫 *Block tizimi*\n\n"
        "Foydalanish: `/find <id|@username>` orqali userni toping va kartadan blok bering."
    )
    await cb.answer()


def register(dp: Dispatcher) -> None:
    dp.include_router(router)
