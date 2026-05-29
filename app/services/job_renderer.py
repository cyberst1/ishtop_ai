"""Premium card formatting (matches the spec exactly)."""
from __future__ import annotations

from app.security.markdown import md_escape

DIVIDER = "━━━━━━━━━━━━━━"


def render_job_card(job: dict, *, balance: float, locked: bool = True) -> tuple[str, bool]:
    title = md_escape(job.get("title", "—"))
    company = md_escape(job.get("company") or "—")
    location = md_escape(job.get("location") or "—")
    salary = md_escape(job.get("salary") or "—")
    work_type = "Remote" if job.get("is_remote") else "Hybrid / Office"

    summary = job.get("ai_summary") or "AI tahlil mavjud emas."
    match = job.get("ai_match_score") or 0
    risk = job.get("ai_scam_risk") or 0

    body = (
        f"{DIVIDER}\n"
        f"💻 *{title}*\n"
        f"🏢 {company}\n"
        f"📍 {location}\n"
        f"💰 {salary}\n"
        f"🌍 {work_type}\n\n"
        f"🧠 *AI Analiz:*\n{md_escape(summary)}\n\n"
        f"📌 Moslik: *{match}%*\n"
        f"🚨 Scam Risk: *{risk}%*\n\n"
    )
    if locked:
        body += f"🪙 Ochish narxi: *2 coin*\n"
        body += f"💳 Balansingiz: *{round(balance, 2)}*\n"
        body += DIVIDER
    else:
        url = job.get("url", "")
        body += f"🔗 [Havola]({url})\n" + DIVIDER

    return body, locked
