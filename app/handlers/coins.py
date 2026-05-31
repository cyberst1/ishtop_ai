"""
User-facing coin info.

No purchase requests are created. The user simply sees the packages + price,
pays the admin card-to-card, then messages the admin. The admin credits the
coins manually (user card → 🪙 Coin qo'shish, or /coin <id> <amount>).
"""
from __future__ import annotations

from aiogram import Dispatcher, F, Router
from aiogram.types import CallbackQuery

from app.keyboards import earn_kb, packages_kb
from app.locales import T
from app.services.coin_packages import get_package

router = Router(name="coins")


@router.callback_query(F.data == "earn:buy")
async def show_packages(cb: CallbackQuery) -> None:
    await cb.message.answer(T["coins_packages_header"], reply_markup=packages_kb())
    await cb.answer()


@router.callback_query(F.data == "earn:back")
async def back_to_earn(cb: CallbackQuery) -> None:
    await cb.message.answer(T["earn_header"], reply_markup=earn_kb())
    await cb.answer()


@router.callback_query(F.data.startswith("buy:"))
async def pick_package(cb: CallbackQuery) -> None:
    slug = cb.data.split(":", 1)[1]
    pkg = get_package(slug)
    if pkg is None:
        await cb.answer(T["error_generic"], show_alert=True)
        return

    price_str = f"{pkg.price:,}".replace(",", " ")
    bonus_line = f"\n🎁 Bonus: *+{pkg.bonus} coin* (jami {pkg.total_coins})" if pkg.bonus else ""
    await cb.message.answer(
        T["coins_buy_instructions"].format(
            coins=pkg.coins,
            price=price_str,
            bonus=bonus_line,
            user_id=cb.from_user.id,
        ),
        reply_markup=_contact_admin_kb(),
        disable_web_page_preview=True,
    )
    await cb.answer()


def _contact_admin_kb():
    from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
    from app.locales.uz import SUPPORT_URL
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📞 Adminga yozish", url=SUPPORT_URL)],
        [InlineKeyboardButton(text=T["back"], callback_data="earn:buy")],
    ])


def register(dp: Dispatcher) -> None:
    dp.include_router(router)
