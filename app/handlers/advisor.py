"""
ISH TOP AI — general AI assistant (chat + career).

Access:
  • Premium+ → unlimited
  • Everyone else → 2 free messages (lifetime trial), then upgrade prompt.

UX:
  • On message → send a "✍️ Xabar yuborildi, javob yozilmoqda" status (with an
    optional sticker if AI_TYPING_STICKER_ID is configured) + typing action.
  • Replace the status with the real answer when it arrives.
"""
from __future__ import annotations

import asyncio

from aiogram import Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.bot.states import AdvisorSG
from app.config import settings
from app.locales import T
from app.security.sanitizer import sanitize_query
from app.services.assistant import AssistantService

router = Router(name="advisor")


@router.message(F.text == T["btn_advisor"])
@router.message(Command("ai"))
async def open_ai(message: Message, state: FSMContext) -> None:
    allowed, reason, remaining = await AssistantService.access(message.from_user.id)
    if not allowed:
        await message.answer(T["ai_trial_exhausted"])
        return
    await state.set_state(AdvisorSG.asking)
    if reason == "premium":
        await message.answer(T["ai_prompt_premium"])
    else:
        await message.answer(T["ai_prompt_trial"].format(remaining=remaining))


@router.message(AdvisorSG.asking, F.text)
async def ask_ai(message: Message, state: FSMContext) -> None:
    # Ignore reply-keyboard buttons so the user can navigate away mid-chat.
    text = (message.text or "").strip()
    menu_buttons = {
        T["btn_search"], T["btn_advisor"], T["btn_earn"],
        T["btn_plans"], T["btn_profile"], T["btn_help"],
    }
    if text in menu_buttons:
        await state.clear()
        return  # let the dedicated handler pick it up on the next update

    allowed, reason, remaining = await AssistantService.access(message.from_user.id)
    if not allowed:
        await state.clear()
        await message.answer(T["ai_trial_exhausted"])
        return

    query = sanitize_query(text)
    if not query:
        await message.answer(T["ai_empty_query"])
        return

    # ---- "message sent / AI is typing" status ----
    status_msg = await _send_typing_status(message)
    try:
        await message.bot.send_chat_action(message.chat.id, action="typing")
    except Exception:
        pass

    answer = await AssistantService.ask(message.from_user.id, query)

    # remove status
    if status_msg is not None:
        try:
            await status_msg.delete()
        except Exception:
            pass

    await message.answer(answer, disable_web_page_preview=True)

    # ---- trial footer ----
    if reason == "trial":
        # recompute remaining after this message
        _, _, rem = await AssistantService.access(message.from_user.id)
        if rem > 0:
            await message.answer(T["ai_trial_remaining"].format(remaining=rem))
        else:
            await state.clear()
            await message.answer(T["ai_trial_just_ended"])


async def _send_typing_status(message: Message):
    """Send the 'message sent, AI is writing' status (+ optional sticker)."""
    sticker_id = settings.ai_typing_sticker_id
    if sticker_id:
        try:
            await message.answer_sticker(sticker_id)
        except Exception:
            pass
    try:
        return await message.answer(T["ai_thinking"])
    except Exception:
        return None


def register(dp: Dispatcher) -> None:
    dp.include_router(router)
