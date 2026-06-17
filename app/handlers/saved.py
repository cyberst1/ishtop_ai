"""View user's saved jobs — paginated and full-card detail."""
from __future__ import annotations

from aiogram import Dispatcher, F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from app.database.engine import get_db
from app.database.repositories import JobsRepo
from app.locales import T
from app.services.job_renderer import render_job_card

router = Router(name="saved")


def _saved_list_kb(jobs: list, page: int, total_pages: int) -> InlineKeyboardMarkup:
    rows = []
    for i, j in enumerate(jobs, 1):
        title = (j["title"] or "—")[:40]
        rows.append([InlineKeyboardButton(
            text=f"{i}. {title}",
            callback_data=f"saved:open:{j['id']}",
        )])
    nav = []
    if page > 1:
        nav.append(InlineKeyboardButton(text="◀️", callback_data=f"saved:page:{page-1}"))
    nav.append(InlineKeyboardButton(text=f"{page}/{total_pages}", callback_data="noop"))
    if page < total_pages:
        nav.append(InlineKeyboardButton(text="▶️", callback_data=f"saved:page:{page+1}"))
    if nav:
        rows.append(nav)
    rows.append([InlineKeyboardButton(text=T["back"], callback_data="profile:home")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _job_detail_kb(job_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🗑 O'chirish", callback_data=f"saved:del:{job_id}"),
            InlineKeyboardButton(text=T["back"], callback_data="saved:list:1"),
        ],
    ])


PAGE_SIZE = 5


async def _get_saved_page(user_id: int, page: int):
    db = get_db()
    rows = await db.fetchall(
        """SELECT j.* FROM saved_jobs s
           JOIN jobs j ON j.id = s.job_id
           WHERE s.user_id = ?
           ORDER BY s.created_at DESC
           LIMIT ? OFFSET ?""",
        (user_id, PAGE_SIZE, (page - 1) * PAGE_SIZE),
    )
    total_row = await db.fetchone(
        "SELECT COUNT(*) AS c FROM saved_jobs WHERE user_id = ?", (user_id,)
    )
    total = total_row["c"] if total_row else 0
    pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
    return rows, total, pages


@router.callback_query(F.data == "profile:saved")
@router.callback_query(F.data.startswith("saved:list:"))
async def show_saved(cb: CallbackQuery) -> None:
    page = 1
    if cb.data.startswith("saved:list:"):
        try:
            page = max(1, int(cb.data.split(":")[2]))
        except (ValueError, IndexError):
            page = 1

    rows, total, pages = await _get_saved_page(cb.from_user.id, page)
    if total == 0:
        try:
            await cb.message.edit_text(T["saved_empty"])
        except Exception:
            await cb.message.answer(T["saved_empty"])
        await cb.answer()
        return

    text = T["saved_list_header"].format(total=total, page=page, pages=pages)
    try:
        await cb.message.edit_text(text, reply_markup=_saved_list_kb(rows, page, pages))
    except Exception:
        await cb.message.answer(text, reply_markup=_saved_list_kb(rows, page, pages))
    await cb.answer()


@router.callback_query(F.data.startswith("saved:page:"))
async def page_saved(cb: CallbackQuery) -> None:
    try:
        page = max(1, int(cb.data.split(":")[2]))
    except (ValueError, IndexError):
        page = 1
    rows, total, pages = await _get_saved_page(cb.from_user.id, page)
    text = T["saved_list_header"].format(total=total, page=page, pages=pages)
    try:
        await cb.message.edit_text(text, reply_markup=_saved_list_kb(rows, page, pages))
    except Exception:
        pass
    await cb.answer()


@router.callback_query(F.data.startswith("saved:open:"))
async def open_saved(cb: CallbackQuery) -> None:
    job_id = cb.data.split(":", 2)[2]
    job = await JobsRepo.get(job_id)
    if not job:
        await cb.answer(T["error_generic"], show_alert=True)
        return
    text, _ = render_job_card(dict(job))
    try:
        await cb.message.edit_text(text, reply_markup=_job_detail_kb(job_id),
                                   disable_web_page_preview=True)
    except Exception:
        await cb.message.answer(text, reply_markup=_job_detail_kb(job_id),
                                disable_web_page_preview=True)
    await cb.answer()


@router.callback_query(F.data.startswith("saved:del:"))
async def delete_saved(cb: CallbackQuery) -> None:
    job_id = cb.data.split(":", 2)[2]
    await get_db().execute(
        "DELETE FROM saved_jobs WHERE user_id = ? AND job_id = ?",
        (cb.from_user.id, job_id),
    )
    await cb.answer(T["saved_deleted"], show_alert=False)
    # Re-render the list
    rows, total, pages = await _get_saved_page(cb.from_user.id, 1)
    if total == 0:
        try:
            await cb.message.edit_text(T["saved_empty"])
        except Exception:
            pass
        return
    text = T["saved_list_header"].format(total=total, page=1, pages=pages)
    try:
        await cb.message.edit_text(text, reply_markup=_saved_list_kb(rows, 1, pages))
    except Exception:
        pass


@router.callback_query(F.data == "noop")
async def noop(cb: CallbackQuery) -> None:
    await cb.answer()


def register(dp: Dispatcher) -> None:
    dp.include_router(router)
