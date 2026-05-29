from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.locales import T


def role_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=T["btn_role_jobseeker"], callback_data="role:jobseeker")],
        [InlineKeyboardButton(text=T["btn_role_employer"], callback_data="role:employer")],
    ])


def job_card_kb(job_id: str, locked: bool = False) -> InlineKeyboardMarkup:
    """All cards are unlocked now — `locked` parameter kept for back-compat."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=T["btn_job_save"], callback_data=f"job:save:{job_id}"),
            InlineKeyboardButton(text=T["btn_job_next"], callback_data="job:next"),
        ],
    ])


def browsing_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=T["btn_job_next"], callback_data="job:next")],
        [InlineKeyboardButton(text=T["cancel"], callback_data="search:cancel")],
    ])
