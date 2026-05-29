"""Search flow: role → query → AI parse → aggregate → render premium cards."""
from __future__ import annotations

from aiogram import Dispatcher, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.bot.states import SearchSG
from app.config import settings
from app.database.repositories import JobsRepo, SearchesRepo, UsersRepo
from app.keyboards import job_card_kb, role_kb
from app.locales import T
from app.security.sanitizer import sanitize_query
from app.services.coin_economy import CoinEconomy
from app.services.job_renderer import render_job_card
from app.services.search_aggregator import SearchAggregator
from app.services.subscriptions import SubscriptionService
from app.utils.logger import logger

router = Router(name="search")


@router.message(F.text == T["btn_search"])
async def open_search(message: Message, state: FSMContext) -> None:
    await state.set_state(SearchSG.role)
    await message.answer(T["search_who_are_you"], reply_markup=role_kb())


@router.callback_query(F.data.startswith("role:"))
async def pick_role(cb: CallbackQuery, state: FSMContext) -> None:
    role = cb.data.split(":", 1)[1]
    await state.update_data(role=role)
    await state.set_state(SearchSG.query)
    await cb.message.edit_text(T["search_query_prompt"])
    await cb.answer()


@router.message(SearchSG.query, F.text)
async def do_search(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id

    # 1. Daily-limit check for free plan
    if not await SubscriptionService.is_premium(user_id):
        used = await SearchesRepo.count_today(user_id)
        if used >= settings.free_daily_searches:
            await message.answer(T["search_daily_limit"].format(limit=settings.free_daily_searches))
            await state.clear()
            return

    raw = message.text or ""
    query = sanitize_query(raw)
    if not query:
        await message.answer(T["search_off_topic"])
        return

    data = await state.get_data()
    role = data.get("role", "jobseeker")

    await message.answer(T["search_searching"])

    aggregator = SearchAggregator()
    jobs, keywords = await aggregator.search(query, role=role)

    await SearchesRepo.log(user_id, query, role, ",".join(keywords), len(jobs))
    logger.info("search.done", extra={"user_id": user_id, "n": len(jobs), "kw": keywords})

    if not jobs:
        await message.answer(T["search_no_results"])
        await state.clear()
        return

    # Persist + queue jobs in FSM
    await JobsRepo.upsert_many(jobs)
    await state.update_data(jobs=[j["id"] for j in jobs], idx=0)
    await state.set_state(SearchSG.browsing)
    await _show_current(message, state)


async def _show_current(target, state: FSMContext) -> None:
    data = await state.get_data()
    ids = data.get("jobs", [])
    idx = data.get("idx", 0)
    if idx >= len(ids):
        await target.answer("✅ Hammasini ko‘rdingiz.")
        await state.clear()
        return
    job = await JobsRepo.get(ids[idx])
    if job is None:
        await state.update_data(idx=idx + 1)
        await _show_current(target, state)
        return

    user_id = (target.from_user.id if isinstance(target, Message) else target.message.chat.id)
    balance = await CoinEconomy.balance(user_id)
    text, locked = render_job_card(dict(job), balance=balance, locked=True)
    if isinstance(target, Message):
        await target.answer(text, reply_markup=job_card_kb(job["id"], locked=locked))
    else:
        await target.message.answer(text, reply_markup=job_card_kb(job["id"], locked=locked))


@router.callback_query(F.data == "job:next")
async def next_job(cb: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    await state.update_data(idx=data.get("idx", 0) + 1)
    await cb.answer()
    await _show_current(cb, state)


@router.callback_query(F.data == "search:cancel")
async def cancel_search(cb: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await cb.message.edit_text("❌ Qidiruv bekor qilindi.")
    await cb.answer()


@router.callback_query(F.data.startswith("unlock:"))
async def unlock_job(cb: CallbackQuery) -> None:
    job_id = cb.data.split(":", 1)[1]
    user_id = cb.from_user.id
    ok, balance = await CoinEconomy.spend(user_id, settings.job_unlock_cost,
                                          reason="job_unlock", related_id=job_id)
    if not ok:
        await cb.answer(T["job_insufficient_coins"].format(balance=balance), show_alert=True)
        return
    job = await JobsRepo.get(job_id)
    if job is None:
        await cb.answer(T["error_generic"], show_alert=True)
        return
    text, _ = render_job_card(dict(job), balance=balance, locked=False)
    await cb.message.edit_text(text, reply_markup=job_card_kb(job_id, locked=False))
    await cb.answer(T["job_unlocked"])


@router.callback_query(F.data.startswith("job:save:"))
async def save_job(cb: CallbackQuery) -> None:
    job_id = cb.data.split(":", 2)[2]
    await JobsRepo.save_for_user(cb.from_user.id, job_id)
    await cb.answer(T["job_saved"])


@router.callback_query(F.data.startswith("job:contact:"))
async def show_contact(cb: CallbackQuery) -> None:
    job_id = cb.data.split(":", 2)[2]
    job = await JobsRepo.get(job_id)
    if job is None:
        await cb.answer(T["error_generic"], show_alert=True)
        return
    contact = job["contact"] or job["url"]
    await cb.answer(f"📞 {contact}", show_alert=True)


@router.callback_query(F.data.startswith("job:details:"))
async def show_details(cb: CallbackQuery) -> None:
    job_id = cb.data.split(":", 2)[2]
    job = await JobsRepo.get(job_id)
    if job is None:
        await cb.answer(T["error_generic"], show_alert=True)
        return
    desc = (job["description"] or "")[:1500]
    await cb.message.answer(f"📄 *{job['title']}*\n\n{desc}\n\n🔗 {job['url']}")
    await cb.answer()


def register(dp: Dispatcher) -> None:
    dp.include_router(router)
