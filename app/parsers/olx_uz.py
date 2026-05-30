"""OLX.uz HTML parser (jobs listing — uses /list/q-… URL pattern)."""
from __future__ import annotations

from typing import Any
from urllib.parse import quote_plus

from bs4 import BeautifulSoup

from app.parsers.base import BaseParser, JobNormalizer
from app.utils.logger import logger


class OlxUzParser(BaseParser):
    SOURCE = "olx_uz"
    BASE_URL = "https://www.olx.uz/list/q-{q}/"

    async def search(self, query: str, keywords: list[str]) -> list[dict[str, Any]]:
        url = self.BASE_URL.format(q=quote_plus(query))
        try:
            html = await self._fetch(url)
            if not html:
                return []
            soup = BeautifulSoup(html, "lxml")
        except Exception as e:
            logger.warning("olx_uz.parse_fail", extra={"err": str(e)[:200]})
            return []

        out: list[dict[str, Any]] = []
        cards = soup.select('div[data-cy="l-card"]')[: self.MAX_RESULTS]
        for c in cards:
            title_el = c.select_one('[data-cy="ad-card-title"]') or c.select_one("h6") or c.select_one("h4")
            title = title_el.get_text(strip=True) if title_el else ""

            # link
            link_el = (title_el and title_el.find("a")) or c.find("a")
            href = link_el.get("href") if link_el else None
            if not href:
                continue
            if not href.startswith("http"):
                href = "https://www.olx.uz" + href

            price_el = c.select_one('[data-testid="ad-price"]')
            loc_el = c.select_one('[data-testid="location-date"]')

            location = ""
            if loc_el:
                txt = loc_el.get_text(strip=True)
                # "Toshkent · 12 dekabr" → take left part
                location = txt.split("·")[0].strip()

            out.append(self.normalize({
                "title": title,
                "company": "",
                "location": location,
                "salary": price_el.get_text(strip=True) if price_el else None,
                "url": href.split("?")[0],
                "description": "",
                "is_remote": JobNormalizer.looks_remote(title),
            }))
        return out
