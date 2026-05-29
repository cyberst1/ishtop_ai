from __future__ import annotations

from aiogram import Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.bot.states import BonusChannelAddSG
from app.database.repositories import BonusRepo
from app.locales import T
from app.security.sessions import AdminSessions
from app.security.markdown import md_escape

router = Router(name="admin_bonus_channels")


@router.callback_query(F.data == "adm:bonus")
async def show(cb: CallbackQuery) -> None:
    if not AdminSessions.is_valid(cb.from_user.id):
        await cb.answer(T["admin_session_expired"], show_alert=True)
        return
    rows = await BonusRepo.list_all()
    lines = ["🎁 *Bonus kanallar*\n"]
    for r in rows:
        flag = "🟢" if r["enabled"] else "⚪"
        lines.append(f"{flag} `{r['id']}` · {md_escape(r['title'])} · +{r['reward']} coin")
    lines.append("\n➕ Qo‘shish: `/bonus_add`")
    lines.append("➖ O‘chirish: `/bonus_del <id>`")
    await cb.message.edit_text("\n".join(lines))
    await cb.answer()


@router.message(Command("bonus_add"))
async def bonus_add(message: Message, state: FSMContext) -> None:
    if not AdminSessions.is_valid(message.from_user.id):
        return
    await state.set_state(BonusChannelAddSG.chat_id)
    await message.answer("Chat ID kiriting (kanaldan, masalan -1001234567890):")


@router.message(BonusChannelAddSG.chat_id, F.text)
async def take_chat_id(message: Message, state: FSMContext) -> None:
    try:
        chat_id = int(message.text.strip())
    except (ValueError, AttributeError):
        await message.answer("❌ Noto‘g‘ri ID.")
        return
    await state.update_data(chat_id=chat_id)
    await state.set_state(BonusChannelAddSG.title)
    await message.answer("Kanal sarlavhasini kiriting:")


@router.message(BonusChannelAddSG.title, F.text)
async def take_title(message: Message, state: FSMContext) -> None:
    await state.update_data(title=message.text.strip())
    await state.set_state(BonusChannelAddSG.invite_link)
    await message.answer("Invite havola (https://t.me/...) kiriting:")


@router.message(BonusChannelAddSG.invite_link, F.text)
async def take_link(message: Message, state: FSMContext) -> None:
    link = message.text.strip()
    if not link.startswith("https://t.me/"):
        await message.answer("❌ Noto‘g‘ri havola.")
        return
    data = await state.get_data()
    await BonusRepo.add(data["chat_id"], data["title"], link, reward=0.5)
    await state.clear()
    await message.answer("✅ Kanal qo‘shildi.")


@router.message(Command("bonus_del"))
async def bonus_del(message: Message) -> None:
    if not AdminSessions.is_valid(message.from_user.id):
        return
    parts = (message.text or "").split()
    if len(parts) < 2 or not parts[1].isdigit():
        await message.answer("Foydalanish: `/bonus_del 1`")
        return
    await BonusRepo.remove(int(parts[1]))
    await message.answer("✅ O‘chirildi.")


def register(dp: Dispatcher) -> None:
    dp.include_router(router)
