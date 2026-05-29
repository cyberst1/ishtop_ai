"""Admin broadcast with progress + anti-flood (30 msg/s)."""
from __future__ import annotations

import asyncio

from aiogram import Bot, Dispatcher, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.bot.states import AdminBroadcastSG
from app.database.engine import get_db
from app.database.repositories import AdminLogsRepo
from app.locales import T
from app.security.sessions import AdminSessions
from app.utils.logger import logger

router = Router(name="admin_broadcast")


@router.callback_query(F.data == "adm:bcast")
async def open_bcast(cb: CallbackQuery, state: FSMContext) -> None:
    if not AdminSessions.is_valid(cb.from_user.id):
        await cb.answer(T["admin_session_expired"], show_alert=True)
        return
    await state.set_state(AdminBroadcastSG.text)
    await cb.message.answer("📢 *Xabar yuborish*\n\nMatnni yuboring (markdown qo‘llab quvvatlanadi):")
    await cb.answer()


@router.message(AdminBroadcastSG.text, F.text)
async def take_text(message: Message, state: FSMContext) -> None:
    if not AdminSessions.is_valid(message.from_user.id):
        return
    await state.update_data(text=message.text)
    await state.set_state(AdminBroadcastSG.confirm)
    await message.answer(
        "Tasdiqlash uchun `START` deb yozing yoki `/cancel` bilan bekor qiling."
    )


@router.message(AdminBroadcastSG.confirm, F.text.casefold() == "start")
async def run_bcast(message: Message, state: FSMContext, bot: Bot) -> None:
    data = await state.get_data()
    text = data["text"]
    await state.clear()
    db = get_db()
    rows = await db.fetchall("SELECT user_id FROM users WHERE is_blocked = 0")
    user_ids = [r["user_id"] for r in rows]
    sent = 0
    failed = 0
    progress = await message.answer(f"📤 0 / {len(user_ids)}")
    await db.execute(
        "INSERT INTO broadcasts (admin_id, text, sent_count, failed_count) VALUES (?, ?, 0, 0)",
        (message.from_user.id, text),
    )
    for i, uid in enumerate(user_ids, 1):
        try:
            await bot.send_message(uid, text)
            sent += 1
        except Exception as e:
            failed += 1
            logger.warning("bcast.fail", extra={"user_id": uid, "err": str(e)[:200]})
        if i % 25 == 0:
            try:
                await progress.edit_text(f"📤 {i} / {len(user_ids)} (✅ {sent} ❌ {failed})")
            except Exception:
                pass
        await asyncio.sleep(0.05)  # ~20 msg/s — safe under Telegram limits
    await db.execute(
        """UPDATE broadcasts SET sent_count = ?, failed_count = ?, finished_at = CURRENT_TIMESTAMP
           WHERE id = (SELECT MAX(id) FROM broadcasts WHERE admin_id = ?)""",
        (sent, failed, message.from_user.id),
    )
    await AdminLogsRepo.log(message.from_user.id, "broadcast",
                            payload=f"sent={sent} failed={failed}")
    await progress.edit_text(f"✅ Yuborildi: *{sent}* / ❌ Xato: *{failed}*")


def register(dp: Dispatcher) -> None:
    dp.include_router(router)
