"""
Premium job-card formatting.

User-requested format:
  ELON NOMI       — title
  QAYERDAN OLINGAN — source (HH.uz, OLX, LinkedIn, ...)
  XAQIDA          — short description
  BOG'LANISH      — contact / link (hidden until unlocked)
  AI MASLAHATI    — short AI tip
"""
from __future__ import annotations

from app.security.markdown import md_escape
from app.utils.text import truncate

DIVIDER = "━━━━━━━━━━━━━━━━━━━━━━━━"

_SOURCE_LABEL = {
    "hh_uz":     "HH.uz",
    "olx_uz":    "OLX.uz",
    "jooble":    "Jooble",
    "linkedin":  "LinkedIn",
    "indeed":    "Indeed",
    "tg":        "Telegram kanali",
}


def _source_label(src: str) -> str:
    return _SOURCE_LABEL.get(src, (src or "—").upper())


def _short_desc(job: dict, limit: int = 220) -> str:
    text = (job.get("description") or "").strip()
    if not text:
        # build a 1-line fallback from company / location / salary
        bits = [job.get("company"), job.get("location"), job.get("salary")]
        text = " · ".join(b for b in bits if b)
    return truncate(text, limit) or "—"


def _ai_tip(job: dict) -> str:
    """Short AI advice line. Falls back to a heuristic when AI summary is empty."""
    summary = (job.get("ai_summary") or "").strip()
    if summary:
        return truncate(summary, 200)

    title = (job.get("title") or "").lower()
    desc = (job.get("description") or "").lower()
    blob = title + " " + desc

    tips = []
    if "junior" in blob or "internship" in blob or "stajirovka" in blob:
        tips.append("✅ Yangi boshlovchilarga mos")
    if any(k in blob for k in ("remote", "uydan", "uyda", "udalyon", "masofadan")):
        tips.append("🌍 Remote imkoniyati bor")
    if any(k in blob for k in ("english", "ingliz")):
        tips.append("🌐 Ingliz tili kerak bo'lishi mumkin")
    if any(k in blob for k in ("docker", "kubernetes", "devops")):
        tips.append("⚙️ DevOps ko'nikmalari foydali")
    if not tips:
        tips.append("💼 E'lonni diqqat bilan o'qib chiqing")

    risk = job.get("ai_scam_risk") or 0
    if risk and risk >= 60:
        tips.append("⚠️ Scam riski yuqori — ehtiyot bo'ling")

    return "  ·  ".join(tips)


def render_job_card(job: dict, *, balance: float, locked: bool = True) -> tuple[str, bool]:
    """
    Returns (text, locked).

    Layout (mobile-friendly, premium look):

        ━━━━━━━━━━━━━━━━━━━━━━━━
        💼  *ELON NOMI*
        Python Backend Developer

        🏷  *QAYERDAN OLINGAN*
        HH.uz

        📝  *XAQIDA*
        ...short description...

        📞  *BOG'LANISH*
        🔒 Ochish narxi: 2 coin    (or contact when unlocked)

        🧠  *AI MASLAHATI*
        ...one-line tip...
        ━━━━━━━━━━━━━━━━━━━━━━━━
    """
    title = md_escape(job.get("title") or "—")
    source = md_escape(_source_label(job.get("source") or ""))
    desc = md_escape(_short_desc(job))
    tip = md_escape(_ai_tip(job))

    if locked:
        contact_line = (
            f"🔒 Ochish narxi: *2 coin*\n"
            f"💳 Balansingiz: *{round(balance, 2)}* coin\n"
            f"⬇️  Tugmani bosing: «🔓 Ochish (2 coin)»"
        )
    else:
        url = job.get("url") or ""
        contact = job.get("contact") or url
        contact_line = f"[🔗 Havola]({url})\n📞 {md_escape(contact)}"

    body = (
        f"{DIVIDER}\n"
        f"💼  *ELON NOMI*\n{title}\n\n"
        f"🏷  *QAYERDAN OLINGAN*\n{source}\n\n"
        f"📝  *XAQIDA*\n{desc}\n\n"
        f"📞  *BOG'LANISH*\n{contact_line}\n\n"
        f"🧠  *AI MASLAHATI*\n{tip}\n"
        f"{DIVIDER}"
    )
    return body, locked
