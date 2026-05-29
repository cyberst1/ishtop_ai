from __future__ import annotations

from aiogram import Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.types import Message

from app.locales import T

router = Router(name="help")


@router.message(F.text == T["btn_help"])
@router.message(Command("help"))
async def show_help(message: Message) -> None:
    await message.answer(T["help_text"])


def register(dp: Dispatcher) -> None:
    dp.include_router(router)
