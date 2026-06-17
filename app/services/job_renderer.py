"""
Premium job-card formatting.

Layout (mobile-first, scannable):

  💼  Python Backend Developer
  ───────────────────────────
  🏢  IT Park Rezident
  📍  Toshkent
  💰  8–15 mln so'm
  🌍  Masofaviy (remote)
  🔎  Manba: OLX.uz

  📝  Tavsif
  …short description…

  📞  Bog'lanish
  🔗 Havola · 📱 +998 …

  🧠  AI maslahati
  …one-line tip…

Everything is visible — contact info is FREE. The search itself costs coins.
"""
from __future__ import annotations

from app.security.markdown import md_escape
from app.utils.text import truncate

THIN = "──────────────────────"

_SOURCE_LABEL = {
    "hh_uz":        "HH.uz",
    "olx_uz":       "OLX.uz",
    "osonish_uz":   "Osonish.uz",
    "ishkerak_uz":  "Ish-kerak.uz",
    "jooble":       "Jooble",
    "linkedin":     "LinkedIn",
    "indeed":       "Indeed",
    "tg":           "Telegram kanali",
}


def _source_label(src: str) -> str:
    return _SOURCE_LABEL.get(src, (src or "—").upper())


def _short_desc(job: dict, limit: int = 240) -> str:
    text = (job.get("description") or "").strip()
    if not text:
        return ""
    return truncate(text, limit)


def _ai_tip(job: dict) -> str:
    summary = (job.get("ai_summary") or "").strip()
    if summary:
        return truncate(summary, 200)

    blob = ((job.get("title") or "") + " " + (job.get("description") or "")).lower()
    tips = []
    if any(k in blob for k in ("junior", "internship", "stajirovka", "amaliyot")):
        tips.append("✅ Yangi boshlovchilarga mos")
    if any(k in blob for k in ("remote", "uydan", "uyda", "udalyon", "masofadan")):
        tips.append("🌍 Masofadan ishlash mumkin")
    if any(k in blob for k in ("english", "ingliz")):
        tips.append("🌐 Ingliz tili foydali")
    if any(k in blob for k in ("docker", "kubernetes", "devops")):
        tips.append("⚙️ DevOps ko'nikmalari ortiqcha bo'lmaydi")
    if any(k in blob for k in ("senior", "lead", "tajribali")):
        tips.append("📈 Tajriba talab qilinadi")
    if not tips:
        tips.append("💼 E'lonni diqqat bilan o'qing va tez murojaat qiling")

    risk = job.get("ai_scam_risk") or 0
    if risk and risk >= 60:
        tips.append("⚠️ Ehtiyot bo'ling — shubhali e'lon bo'lishi mumkin")
    return "  ·  ".join(tips)


def _contact_block(job: dict) -> str:
    url = (job.get("url") or "").strip()
    contact = (job.get("contact") or "").strip()
    parts = []
    if url:
        parts.append(f"[🔗 Havolani ochish]({url})")
    if contact and contact != url:
        parts.append(f"📱 {md_escape(contact)}")
    return "\n".join(parts) if parts else "—"


def render_job_card(job: dict, *, balance: float = 0.0, locked: bool = False
                    ) -> tuple[str, bool]:
    """Render a fully-visible premium card. `locked` is ignored (always False)."""
    title = md_escape(job.get("title") or "—")
    company = md_escape((job.get("company") or "").strip())
    location = md_escape((job.get("location") or "").strip())
    salary = md_escape((job.get("salary") or "").strip())
    source = md_escape(_source_label(job.get("source") or ""))
    desc = md_escape(_short_desc(job))
    tip = md_escape(_ai_tip(job))
    contact = _contact_block(job)

    # --- Header ---
    lines = [f"💼  *{title}*", THIN]

    # --- Meta block (only show fields we actually have) ---
    if company:
        lines.append(f"🏢  {company}")
    if location:
        lines.append(f"📍  {location}")
    if salary:
        lines.append(f"💰  {salary}")
    if job.get("is_remote"):
        lines.append("🌍  Masofaviy (remote)")
    lines.append(f"🔎  Manba: {source}")

    # --- Description ---
    if desc:
        lines.append("")
        lines.append("📝  *Tavsif*")
        lines.append(desc)

    # --- Contact ---
    lines.append("")
    lines.append("📞  *Bog'lanish*")
    lines.append(contact)

    # --- AI tip ---
    lines.append("")
    lines.append("🧠  *AI maslahati*")
    lines.append(tip)

    return "\n".join(lines), False
