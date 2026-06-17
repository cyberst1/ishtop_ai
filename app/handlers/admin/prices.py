"""Admin: edit runtime prices / economy via inline pickers."""
from __future__ import annotations

from aiogram import Dispatcher, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.bot.states import AdminPriceSG
from app.database.repositories import AdminLogsRepo
from app.locales import T
from app.security.sessions import AdminSessions
from app.services.runtime_config import EDITABLE_KEYS, runtime

router = Router(name="admin_prices")


def _guard(uid: int) -> bool:
    return AdminSessions.is_valid(uid)


@router.callback_query(F.data.startswith("adm:price:edit:"))
async def start_edit(cb: CallbackQuery, state: FSMContext) -> None:
    if not _guard(cb.from_user.id):
        await cb.answer(T["admin_session_expired"], show_alert=True)
        return

    key = cb.data.split(":")[3]
    if key not in EDITABLE_KEYS:
        await cb.answer("❌", show_alert=False)
        return

    cur = getattr(runtime, key)
    await state.update_data(price_key=key)
    await state.set_state(AdminPriceSG.value)
    await cb.message.answer(
        T["admin_price_prompt"].format(
            label=runtime.label(key), current=cur,
        )
    )
    await cb.answer()


@router.message(AdminPriceSG.value, F.text)
async def apply_edit(message: Message, state: FSMContext) -> None:
    if not _guard(message.from_user.id):
        await state.clear()
        return

    raw = (message.text or "").strip().replace(",", ".")
    data = await state.get_data()
    key = data.get("price_key")
    if key not in EDITABLE_KEYS:
        await state.clear()
        return

    typ = EDITABLE_KEYS[key]
    try:
        # cast to the right numeric type
        value = typ(float(raw)) if typ is int else typ(raw)
    except (ValueError, TypeError):
        await message.answer(T["admin_price_bad_value"])
        return

    if value <= 0:
        await message.answer(T["admin_price_bad_value"])
        return

    await runtime.update(key, value, admin_id=message.from_user.id)
    await AdminLogsRepo.log(
        message.from_user.id, "price_update",
        payload=f"{key}={value}",
    )
    await state.clear()

    await message.answer(
        T["admin_price_done"].format(
            label=runtime.label(key), value=value,
        )
    )


def register(dp: Dispatcher) -> None:
    dp.include_router(router)
