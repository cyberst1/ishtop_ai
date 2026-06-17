from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.locales import T


def role_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=T["btn_role_jobseeker"], callback_data="role:jobseeker")],
        [InlineKeyboardButton(text=T["btn_role_employer"], callback_data="role:employer")],
    ])


def job_card_kb(job_id: str, *, has_next: bool = True) -> InlineKeyboardMarkup:
    """Job card actions: Save, Next (if any), New search."""
    rows = [[InlineKeyboardButton(text=T["btn_job_save"], callback_data=f"job:save:{job_id}")]]
    if has_next:
        rows[0].append(InlineKeyboardButton(text=T["btn_job_next"], callback_data="job:next"))
    rows.append([
        InlineKeyboardButton(text=T["btn_new_search"], callback_data="search:new"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def browsing_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=T["btn_job_next"], callback_data="job:next")],
        [InlineKeyboardButton(text=T["cancel"], callback_data="search:cancel")],
    ])
