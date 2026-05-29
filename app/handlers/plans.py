from __future__ import annotations

from aiogram import Dispatcher, F, Router
from aiogram.types import CallbackQuery, Message

from app.keyboards import plans_kb
from app.locales import T
from app.services.subscriptions import SubscriptionService

router = Router(name="plans")


@router.message(F.text == T["btn_plans"])
@router.callback_query(F.data == "profile:plans")
async def show_plans(event) -> None:
    text = "\n\n".join([T["plans_header"], T["plan_free"], T["plan_premium"], T["plan_premium_plus"]])
    if isinstance(event, Message):
        await event.answer(text, reply_markup=plans_kb())
    else:
        await event.message.answer(text, reply_markup=plans_kb())
        await event.answer()


@router.callback_query(F.data.startswith("plan:buy:"))
async def buy_plan(cb: CallbackQuery) -> None:
    plan = cb.data.split(":", 2)[2]
    # Real payment provider integration goes here (Click, Payme, Telegram Payments).
    # For now we store the request and return contact info.
    await SubscriptionService.start_purchase(cb.from_user.id, plan)
    await cb.message.answer(
        f"💳 *{plan.upper()}* tarifini sotib olish uchun admin bilan bog‘laning: @support"
    )
    await cb.answer()


def register(dp: Dispatcher) -> None:
    dp.include_router(router)
