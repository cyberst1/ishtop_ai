"""Admin: list pending coin purchases + confirm / reject them inline."""
from __future__ import annotations

from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from app.database.repositories import AdminLogsRepo, CoinPurchasesRepo
from app.keyboards.admin import admin_back_kb
from app.locales import T
from app.security.markdown import md_escape
from app.security.sessions import AdminSessions
from app.services import PurchaseService

router = Router(name="admin_payments")


def _guard(uid: int) -> bool:
    return AdminSessions.is_valid(uid)


def _row_kb(purchase_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=f"✅ #{purchase_id} Tasdiqlash",
                                 callback_data=f"adm:pay:ok:{purchase_id}"),
            InlineKeyboardButton(text=f"❌ #{purchase_id} Rad etish",
                                 callback_data=f"adm:pay:no:{purchase_id}"),
        ],
    ])


@router.callback_query(F.data == "adm:pay")
async def list_payments(cb: CallbackQuery) -> None:
    if not _guard(cb.from_user.id):
        await cb.answer(T["admin_session_expired"], show_alert=True)
        return

    rows = await CoinPurchasesRepo.list_pending(20)
    if not rows:
        await cb.message.edit_text(T["admin_payments_empty"], reply_markup=admin_back_kb())
        await cb.answer()
        return

    # Header message
    await cb.message.edit_text(
        T["admin_payments_header"].format(count=len(rows)),
        reply_markup=admin_back_kb(),
    )

    # One follow-up message per pending purchase, each with its own Confirm/Reject row
    for r in rows:
        uname = f"@{r['username']}" if r["username"] else "—"
        full_name = md_escape(r["full_name"] or "—")
        price = f"{r['price']:,}".replace(",", " ")
        body = (
            f"💳 *So'rov #{r['id']}*\n\n"
            f"👤 {full_name} · {md_escape(uname)}\n"
            f"🆔 `{r['user_id']}`\n"
            f"🪙 *{r['coins']} coin* uchun\n"
            f"💵 *{price} so'm*\n"
            f"📅 {r['created_at']}"
        )
        try:
            await cb.message.answer(body, reply_markup=_row_kb(r["id"]))
        except Exception:
            pass

    await cb.answer()


@router.callback_query(F.data.startswith("adm:pay:ok:"))
async def confirm_payment(cb: CallbackQuery, bot: Bot) -> None:
    if not _guard(cb.from_user.id):
        await cb.answer(T["admin_session_expired"], show_alert=True)
        return

    pid = int(cb.data.split(":")[3])
    result = await PurchaseService.confirm(pid, cb.from_user.id, bot)
    if result is None:
        await cb.answer(T["admin_payment_not_found"], show_alert=True)
        return

    await AdminLogsRepo.log(cb.from_user.id, "purchase_confirm",
                            target_user=result["user_id"], payload=str(pid))
    try:
        await cb.message.edit_text(
            T["admin_payment_confirmed"].format(
                id=pid, coins=result["coins"], user_id=result["user_id"],
                balance=round(result["new_balance"], 2),
            ),
        )
    except Exception:
        pass
    await cb.answer("✅ Tasdiqlandi.", show_alert=False)


@router.callback_query(F.data.startswith("adm:pay:no:"))
async def reject_payment(cb: CallbackQuery, bot: Bot) -> None:
    if not _guard(cb.from_user.id):
        await cb.answer(T["admin_session_expired"], show_alert=True)
        return

    pid = int(cb.data.split(":")[3])
    result = await PurchaseService.reject(pid, cb.from_user.id, bot,
                                          reason="admin_reject")
    if result is None:
        await cb.answer(T["admin_payment_not_found"], show_alert=True)
        return

    await AdminLogsRepo.log(cb.from_user.id, "purchase_reject",
                            target_user=result["user_id"], payload=str(pid))
    try:
        await cb.message.edit_text(
            T["admin_payment_rejected"].format(
                id=pid, user_id=result["user_id"], coins=result["coins"],
            ),
        )
    except Exception:
        pass
    await cb.answer("❌ Rad etildi.", show_alert=False)


def register(dp: Dispatcher) -> None:
    dp.include_router(router)
