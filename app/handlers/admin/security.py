from __future__ import annotations

from aiogram import Dispatcher, F, Router
from aiogram.types import CallbackQuery

from app.database.repositories import AdminLogsRepo
from app.locales import T
from app.security.markdown import md_escape
from app.security.sessions import AdminSessions

router = Router(name="admin_security")


@router.callback_query(F.data == "adm:security")
async def show_security(cb: CallbackQuery) -> None:
    if not AdminSessions.is_valid(cb.from_user.id):
        await cb.answer(T["admin_session_expired"], show_alert=True)
        return
    await cb.message.edit_text(
        "🛡 *Security*\n\n"
        "• Bcrypt admin parol\n"
        "• ADMIN_IDS allowlist\n"
        "• Sessiya: 30 daqiqa\n"
        "• AntiFlood: yoqilgan\n"
        "• HMAC callback tokens: yoqilgan\n"
        "• Multi-account aniqlash: yoqilgan\n\n"
        "📂 Loglarni ko‘rish uchun «📂 Loglar» tugmasini bosing."
    )
    await cb.answer()


@router.callback_query(F.data == "adm:logs")
async def show_logs(cb: CallbackQuery) -> None:
    if not AdminSessions.is_valid(cb.from_user.id):
        await cb.answer(T["admin_session_expired"], show_alert=True)
        return
    rows = await AdminLogsRepo.recent(20)
    lines = ["📂 *Oxirgi 20 ta admin log:*\n"]
    for r in rows:
        flag = "✅" if r["success"] else "❌"
        lines.append(
            f"{flag} `{r['created_at']}` · `{r['admin_id']}` · {md_escape(r['action'])}"
        )
    await cb.message.edit_text("\n".join(lines))
    await cb.answer()


def register(dp: Dispatcher) -> None:
    dp.include_router(router)
