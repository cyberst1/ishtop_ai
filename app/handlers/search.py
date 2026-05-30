"""
Search flow:
  role  →  query  →  IntentGuard
                  →  pre-check balance
                  →  aggregate (6 parsers in parallel)
                  →  charge 2 coin (only if results found)
                  →  paginated cards (1/N) with FREE contacts
"""
from __future__ import annotations

from aiogram import Dispatcher, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.ai.intent_guard import IntentGuard
from app.bot.states import SearchSG
from app.config import settings
from app.database.repositories import JobsRepo, SearchesRepo
from app.keyboards import job_card_kb, role_kb
from app.locales import T
from app.security.sanitizer import sanitize_query
from app.services.coin_economy import CoinEconomy
from app.services.job_renderer import render_job_card
from app.services.runtime_config import runtime
from app.services.search_aggregator import SearchAggregator
from app.services.subscriptions import SubscriptionService
from app.utils.logger import logger

router = Router(name="search")


# ─────────────────────────────────────── entry ─────

@router.message(F.text == T["btn_search"])
async def open_search(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(SearchSG.role)
    await message.answer(T["search_who_are_you"], reply_markup=role_kb())


@router.callback_query(F.data.startswith("role:"))
async def pick_role(cb: CallbackQuery, state: FSMContext) -> None:
    role = cb.data.split(":", 1)[1]
    await state.update_data(role=role)
    await state.set_state(SearchSG.query)
    try:
        await cb.message.edit_text(T["search_query_prompt"])
    except Exception:
        await cb.message.answer(T["search_query_prompt"])
    await cb.answer()


# ─────────────────────────────────────── search ─────

@router.message(SearchSG.query, F.text)
async def do_search(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    is_premium = await SubscriptionService.is_premium(user_id)

    # 1. Daily limit (free plan)
    if not is_premium:
        used = await SearchesRepo.count_today(user_id)
        if used >= runtime.free_daily_searches:
            await message.answer(
                T["search_daily_limit"].format(limit=runtime.free_daily_searches)
            )
            await state.clear()
            return

    # 2. Sanitize
    query = sanitize_query(message.text or "")
    if not query:
        await message.answer(T["search_off_topic"])
        return

    # 3. Intent guard
    verdict = await IntentGuard.check(query)
    if not verdict.allowed:
        await message.answer(T["search_off_topic"])
        logger.info(
            "search.rejected_off_topic",
            extra={"user_id": user_id, "reason": verdict.reason, "query": query[:80]},
        )
        return

    # 4. Pre-check balance
    if not is_premium:
        balance = await CoinEconomy.balance(user_id)
        if balance < runtime.search_cost:
            await message.answer(
                T["search_insufficient_coins"].format(
                    balance=round(balance, 2), cost=runtime.search_cost
                )
            )
            await state.clear()
            return

    data = await state.get_data()
    role = data.get("role", "jobseeker")

    # 5. Run parsers (with typing indicator)
    progress = await message.answer(T["search_searching"])
    try:
        await message.bot.send_chat_action(message.chat.id, action="typing")
    except Exception:
        pass

    aggregator = SearchAggregator()
    jobs, keywords = await aggregator.search(query, role=role)

    await SearchesRepo.log(user_id, query, role, ",".join(keywords), len(jobs))
    logger.info(
        "search.done",
        extra={"user_id": user_id, "n": len(jobs), "kw": keywords[:5]},
    )

    # delete the "searching..." message
    try:
        await progress.delete()
    except Exception:
        pass

    # 6. No results → no charge
    if not jobs:
        await message.answer(T["search_no_results"])
        await state.clear()
        return

    # 7. Charge 2 coin
    if not is_premium:
        ok, new_balance = await CoinEconomy.spend(
            user_id, runtime.search_cost,
            reason="search", related_id=query[:40],
        )
        if not ok:
            await message.answer(
                T["search_insufficient_coins"].format(
                    balance=round(new_balance, 2), cost=runtime.search_cost
                )
            )
            await state.clear()
            return
        await message.answer(
            T["search_charged"].format(
                cost=runtime.search_cost,
                balance=round(new_balance, 2),
                count=len(jobs),
            )
        )

    # 8. Persist & start browsing
    await JobsRepo.upsert_many(jobs)
    await state.update_data(jobs=[j["id"] for j in jobs], idx=0, total=len(jobs))
    await state.set_state(SearchSG.browsing)
    await _show_current(message, state)


# ─────────────────────────────────────── browsing ─────

async def _show_current(target, state: FSMContext) -> None:
    data = await state.get_data()
    ids = data.get("jobs", [])
    idx = data.get("idx", 0)
    total = data.get("total", len(ids))

    if idx >= len(ids):
        msg = T["search_all_seen"]
        if isinstance(target, Message):
            await target.answer(msg)
        else:
            try:
                await target.message.answer(msg)
            except Exception:
                pass
        await state.clear()
        return

    job = await JobsRepo.get(ids[idx])
    if job is None:
        await state.update_data(idx=idx + 1)
        await _show_current(target, state)
        return

    pagination = T["job_pagination"].format(idx=idx + 1, total=total)
    text, _ = render_job_card(dict(job))
    text = f"{pagination}\n{text}"
    kb = job_card_kb(job["id"])

    if isinstance(target, Message):
        await target.answer(text, reply_markup=kb, disable_web_page_preview=True)
    else:
        try:
            await target.message.answer(text, reply_markup=kb, disable_web_page_preview=True)
        except Exception:
            pass


@router.callback_query(F.data == "job:next")
async def next_job(cb: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    await state.update_data(idx=data.get("idx", 0) + 1)
    await cb.answer()
    await _show_current(cb, state)


@router.callback_query(F.data == "search:cancel")
async def cancel_search(cb: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    try:
        await cb.message.edit_text("❌ Qidiruv bekor qilindi.")
    except Exception:
        pass
    await cb.answer()


@router.callback_query(F.data.startswith("job:save:"))
async def save_job(cb: CallbackQuery) -> None:
    job_id = cb.data.split(":", 2)[2]
    await JobsRepo.save_for_user(cb.from_user.id, job_id)
    await cb.answer(T["job_saved"], show_alert=False)


def register(dp: Dispatcher) -> None:
    dp.include_router(router)
