"""AI Career Advisor — Premium+ only. Strict career-only intent guard."""
from __future__ import annotations

from aiogram import Dispatcher, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.bot.states import AdvisorSG
from app.locales import T
from app.security.sanitizer import sanitize_query
from app.services.advisor import AdvisorService
from app.services.subscriptions import SubscriptionService

router = Router(name="advisor")


@router.message(F.text == T["btn_advisor"])
async def open_advisor(message: Message, state: FSMContext) -> None:
    if not await SubscriptionService.is_premium_plus(message.from_user.id):
        await message.answer(T["advisor_only_premium_plus"])
        return
    await state.set_state(AdvisorSG.asking)
    await message.answer(T["advisor_prompt"])


@router.message(AdvisorSG.asking, F.text)
async def ask_advisor(message: Message, state: FSMContext) -> None:
    if not await SubscriptionService.is_premium_plus(message.from_user.id):
        await message.answer(T["advisor_only_premium_plus"])
        await state.clear()
        return

    query = sanitize_query(message.text or "")
    if not query:
        await message.answer(T["search_off_topic"])
        return

    answer = await AdvisorService.ask(message.from_user.id, query)
    await message.answer(answer)


def register(dp: Dispatcher) -> None:
    dp.include_router(router)
