from __future__ import annotations

from aiogram import Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from app.ai.client import AIClient
from app.config import settings
from app.database.repositories import AdminLogsRepo
from app.locales import T
from app.security.markdown import md_escape
from app.security.sessions import AdminSessions

router = Router(name="admin_security")


@router.message(Command("ai_test"))
async def ai_test(message: Message) -> None:
    """Diagnose why the AI is silent. Admin-only."""
    if not AdminSessions.is_valid(message.from_user.id):
        await message.answer(T["admin_session_expired"])
        return
    await message.answer("🔍 AI sinovdan o'tkazilmoqda... (30-40 soniya)")
    ok, detail = await AIClient.diagnose()
    flag = "✅" if ok else "❌"
    # Plain text (parse_mode=None) — model names contain '/' ':' '-' and the
    # detail may contain arbitrary error text; avoid any Markdown breakage.
    body = (
        f"{flag} AI DIAGNOSTIKA\n\n"
        f"🔑 Kalit: {'bor' if settings.effective_ai_api_key else 'YO‘Q'}\n"
        f"🌐 URL: {settings.effective_ai_base_url}\n"
        f"🤖 Asosiy model: {settings.effective_ai_model}\n\n"
        f"{detail}"
    )
    await message.answer(body, parse_mode=None)


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
