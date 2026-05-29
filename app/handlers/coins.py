"""User-facing coin purchase flow."""
from __future__ import annotations

from aiogram import Dispatcher, F, Router
from aiogram.types import CallbackQuery

from app.database.repositories import CoinPurchasesRepo
from app.keyboards import packages_kb, payment_made_kb, earn_kb
from app.locales import T
from app.services import PurchaseService

router = Router(name="coins")


@router.callback_query(F.data == "earn:buy")
async def show_packages(cb: CallbackQuery) -> None:
    await cb.message.answer(T["coins_packages_header"], reply_markup=packages_kb())
    await cb.answer()


@router.callback_query(F.data == "earn:back")
async def back_to_earn(cb: CallbackQuery) -> None:
    await cb.message.answer(T["earn_header"], reply_markup=earn_kb())
    await cb.answer()


@router.callback_query(F.data.startswith("buy:cancel:"))
async def cancel_purchase(cb: CallbackQuery) -> None:
    pid = int(cb.data.split(":")[2])
    purchase = await CoinPurchasesRepo.get(pid)
    if purchase and purchase["user_id"] == cb.from_user.id and purchase["status"] == "pending":
        await CoinPurchasesRepo.mark_rejected(pid, cb.from_user.id, "user_cancelled")
        await cb.message.edit_text(T["purchase_cancelled"].format(id=pid))
    await cb.answer()


@router.callback_query(F.data.startswith("buy:"))
async def pick_package(cb: CallbackQuery) -> None:
    parts = cb.data.split(":")
    if len(parts) < 2:
        await cb.answer()
        return
    slug = parts[1]

    result = await PurchaseService.create_request(cb.from_user.id, slug)
    if result is None:
        await cb.answer(T["error_generic"], show_alert=True)
        return

    purchase_id, pkg = result
    price_str = f"{pkg.price:,}".replace(",", " ")
    await cb.message.answer(
        T["purchase_instructions"].format(
            id=purchase_id,
            coins=pkg.coins,
            price=price_str,
        ),
        reply_markup=payment_made_kb(purchase_id),
        disable_web_page_preview=True,
    )
    await cb.answer()


def register(dp: Dispatcher) -> None:
    dp.include_router(router)
