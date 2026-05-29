"""
Telegram channel parser — uses t.me/s/<username> public preview pages.
No API_ID needed for this fallback. For private/auth channels integrate Telethon.
"""
from __future__ import annotations

from typing import Any
from urllib.parse import quote_plus

from bs4 import BeautifulSoup

from app.parsers.base import BaseParser, JobNormalizer
from app.utils.logger import logger

TG_JOB_CHANNELS = [
    "ishtoshkent",
    "ish_uz",
    "remote_ish_uz",
    "vakansiya_uzbekistan",
]


class TelegramChannelsParser(BaseParser):
    SOURCE = "tg"

    async def search(self, query: str, keywords: list[str]) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        q_low = query.lower()
        for ch in TG_JOB_CHANNELS:
            url = f"https://t.me/s/{ch}"
            try:
                html = await self._fetch(url)
                if not html:
                    continue
                soup = BeautifulSoup(html, "lxml")
                posts = soup.select("div.tgme_widget_message_text")[-30:]
                for p in posts:
                    text = p.get_text(" ", strip=True)
                    if not text or q_low not in text.lower():
                        # also accept if any keyword appears
                        if not any(k.lower() in text.lower() for k in keywords):
                            continue
                    parent = p.find_parent("div", class_="tgme_widget_message")
                    href = (parent.get("data-post") if parent else None)
                    full_url = f"https://t.me/{href}" if href else url
                    results.append(self.normalize({
                        "title": text[:120],
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
