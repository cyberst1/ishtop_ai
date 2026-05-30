"""
Telegram channel parser — uses public `t.me/s/<username>` preview pages.
No API key required.  Filters posts by keyword overlap.
"""
from __future__ import annotations

import re
from typing import Any

from bs4 import BeautifulSoup

from app.parsers.base import BaseParser, JobNormalizer
from app.utils.logger import logger

# Curated public Uzbek job channels (verified to exist, public preview).
# Add more in lowercase, no @ prefix.
TG_JOB_CHANNELS = [
    "ishtoshkent",
    "ish_uz",
    "remote_ish_uz",
    "vakansiya_uzbekistan",
    "uzjobs",
    "jobsbox_uz",
    "freelance_uz",
    "dasturchilar_uz",
    "it_uzbekistan",
]


class TelegramChannelsParser(BaseParser):
    SOURCE = "tg"

    async def search(self, query: str, keywords: list[str]) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        # Lowercase keywords for substring matching
        kw_lower = {k.lower() for k in keywords if k}
        # Add the most important original tokens too
        for tok in re.split(r"[^\wʻ']+", query.lower()):
            if len(tok) >= 3:
                kw_lower.add(tok)

        for ch in TG_JOB_CHANNELS:
            if len(results) >= self.MAX_RESULTS:
                break
            url = f"https://t.me/s/{ch}"
            try:
                html = await self._fetch(url)
                if not html:
                    continue
                soup = BeautifulSoup(html, "lxml")
                # Most recent posts (channel pages list newest at the bottom)
                posts = soup.select("div.tgme_widget_message")[-30:]
                for parent in posts:
                    text_el = parent.select_one(".tgme_widget_message_text")
                    if not text_el:
                        continue
                    text = text_el.get_text(" ", strip=True)
                    if not text:
                        continue
                    text_lower = text.lower()
                    # Must match at least one keyword
                    if not any(k in text_lower for k in kw_lower):
                        continue
                    href = parent.get("data-post")
                    full_url = f"https://t.me/{href}" if href else url
                    title = text[:120].rstrip(",.;") + ("..." if len(text) > 120 else "")
                    results.append(self.normalize({
                        "title": title,
                        "company": f"@{ch}",
                        "location": "Uzbekistan",
                        "salary": None,
                        "url": full_url,
                        "description": text[:1500],
                        "contact": full_url,
                        "is_remote": JobNormalizer.looks_remote(text),
                    }))
                    if len(results) >= self.MAX_RESULTS:
                        break
            except Exception as e:
                logger.warning("tg.parse_fail", extra={"ch": ch, "err": str(e)[:200]})
        return results[: self.MAX_RESULTS]
