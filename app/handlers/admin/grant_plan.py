"""Admin: 'Userga tarif ulash' — quick flow inside OBUNA section.

Flow:
  1. Admin clicks ➕ Userga tarif ulash
  2. Bot asks for user ID or @username
  3. Admin types it, bot validates + shows the user card
  4. Admin picks Free / Premium / Premium+ inline
  5. Plan is granted for 30 days, user gets notified

Power-user shortcut:
  /tarif <user_id> <plan>     # plan: free | premium | premium_plus
"""
from __future__ import annotations

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.bot.states import AdminGrantPlanSG
from app.database.repositories import AdminLogsRepo, UsersRepo
from app.keyboards.admin import admin_plan_pick_kb
from app.locales import T
from app.security.markdown import md_escape
from app.security.sessions import AdminSessions
from app.services.runtime_config import runtime
from app.services.subscriptions import SubscriptionService

router = Router(name="admin_grant_plan")

_PLAN_LABEL = {"free": "Free", "premium": "Premium", "premium_plus": "Premium+"}
_VALID_PLANS = set(_PLAN_LABEL.keys())


def _guard(uid: int) -> bool:
    return AdminSessions.is_valid(uid)


# ─────────────────────────── inline trigger from OBUNA ───────────────────────────

@router.callback_query(F.data == "adm:grant_plan_start")
async def grant_start(cb: CallbackQuery, state: FSMContext) -> None:
    if not _guard(cb.from_user.id):
        await cb.answer(T["admin_session_expired"], show_alert=True)
        return
    await state.clear()
    await state.set_state(AdminGrantPlanSG.user_input)
    await cb.message.answer(T["admin_grant_plan_prompt"])
    await cb.answer()


@router.message(AdminGrantPlanSG.user_input, F.text)
async def grant_pick_user(message: Message, state: FSMContext) -> None:
    if not _guard(message.from_user.id):
        await state.clear()
        return

    q = (message.text or "").strip()
    user = None
    if q.startswith("@") or not q.lstrip("-").isdigit():
        user = await UsersRepo.get_by_username(q)
    else:
        try:
            user = await UsersRepo.get(int(q))
        except ValueError:
            user = None

    if not user:
        await message.answer(T["admin_user_not_found"])
        await state.clear()
        return

    await state.clear()
    await message.answer(
        T["admin_grant_plan_pick"].format(
            user_id=user["user_id"],
            username=md_escape(("@" + user["username"]) if user["username"] else "—"),
            full_name=md_escape(user["full_name"] or "—"),
            current_plan=_PLAN_LABEL.get(user["plan"], user["plan"]),
        ),
        reply_markup=admin_plan_pick_kb(user["user_id"]),
    )


# ─────────────────────────── /tarif power command ───────────────────────────

@router.message(Command("tarif"))
async def grant_plan_command(message: Message, bot: Bot) -> None:
    if not _guard(message.from_user.id):
        await message.answer(T["admin_session_expired"])
        return

    parts = (message.text or "").split()
    if len(parts) != 3:
        await message.answer(T["admin_tarif_usage"])
        return
    _, uid_str, plan = parts
    plan = plan.strip().lower()

    if not uid_str.lstrip("-").isdigit() or plan not in _VALID_PLANS:
        await message.answer(T["admin_tarif_usage"])
        return

    uid = int(uid_str)
    if not await UsersRepo.get(uid):
        await message.answer(T["admin_user_not_found"])
        return

    bonus = await SubscriptionService.activate(uid, plan, price=0,
                                               payment_id=f"admin:{message.from_user.id}")
    await AdminLogsRepo.log(message.from_user.id, "grant_plan",
                            target_user=uid, payload=plan)
    await message.answer(
        T["admin_plan_granted"].format(
            user_id=uid, plan=_PLAN_LABEL.get(plan, plan),
            days=int(runtime.plan_duration_days) if plan != "free" else "∞",
            bonus=_bonus_line(bonus),
        )
    )
    try:
        await bot.send_message(
            uid,
            T["user_plan_granted_notify"].format(
                plan=_PLAN_LABEL.get(plan, plan),
                days=int(runtime.plan_duration_days) if plan != "free" else "∞",
                bonus=_bonus_line(bonus),
            ),
        )
    except Exception:
        pass


def _bonus_line(bonus: float) -> str:
    return f"\n🎁 Bonus: +{int(bonus)} coin" if bonus and bonus > 0 else ""


def register(dp: Dispatcher) -> None:
    dp.include_router(router)
