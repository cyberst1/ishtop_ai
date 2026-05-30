"""Admin broadcast: text → confirm → throttled send to all non-blocked users."""
from __future__ import annotations

import asyncio

from aiogram import Bot, Dispatcher, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.bot.states import AdminBroadcastSG
from app.database.engine import get_db
from app.database.repositories import AdminLogsRepo
from app.locales import T
from app.security.sessions import AdminSessions
from app.utils.logger import logger

router = Router(name="admin_broadcast")


def _guard(uid: int) -> bool:
    return AdminSessions.is_valid(uid)


@router.message(AdminBroadcastSG.text, F.text)
async def take_text(message: Message, state: FSMContext) -> None:
    if not _guard(message.from_user.id):
        await state.clear()
        return
    await state.update_data(text=message.text)
    await state.set_state(AdminBroadcastSG.confirm)
    await message.answer(T["admin_broadcast_confirm"])


@router.message(AdminBroadcastSG.confirm, F.text.casefold() == "start")
async def run_bcast(message: Message, state: FSMContext, bot: Bot) -> None:
    data = await state.get_data()
    text = data.get("text", "")
    await state.clear()
    if not text:
        return

    db = get_db()
    rows = await db.fetchall("SELECT user_id FROM users WHERE is_blocked = 0")
    user_ids = [r["user_id"] for r in rows]

    sent = 0
    failed = 0
    progress = await message.answer(T["admin_broadcast_started"].format(total=len(user_ids)))

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
                await progress.edit_text(
                    T["admin_broadcast_progress"].format(
                        i=i, total=len(user_ids), sent=sent, failed=failed,
                    )
                )
            except Exception:
                pass
        await asyncio.sleep(0.05)

    await db.execute(
        """UPDATE broadcasts SET sent_count = ?, failed_count = ?, finished_at = CURRENT_TIMESTAMP
           WHERE id = (SELECT MAX(id) FROM broadcasts WHERE admin_id = ?)""",
        (sent, failed, message.from_user.id),
    )
    await AdminLogsRepo.log(message.from_user.id, "broadcast",
                            payload=f"sent={sent} failed={failed}")
    try:
        await progress.edit_text(T["admin_broadcast_done"].format(sent=sent, failed=failed))
    except Exception:
        pass


def register(dp: Dispatcher) -> None:
    dp.include_router(router)
