"""OLX.uz HTML parser (jobs section)."""
from __future__ import annotations

from typing import Any
from urllib.parse import quote_plus

from bs4 import BeautifulSoup

from app.parsers.base import BaseParser, JobNormalizer
from app.utils.logger import logger


class OlxUzParser(BaseParser):
    SOURCE = "olx_uz"
    BASE_URL = "https://www.olx.uz/ish/q-{q}/"

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
            a = c.find("a")
            href = a.get("href") if a else None
            if not href:
                continue
            if not href.startswith("http"):
                href = "https://www.olx.uz" + href
            title_el = c.select_one("h6") or c.select_one("h4")
            price_el = c.select_one('[data-testid="ad-price"]')
            loc_el = c.select_one('p[data-testid="location-date"]')
            title = (title_el.get_text(strip=True) if title_el else "")
            out.append(self.normalize({
                "title": title,
                "company": "",
                "location": loc_el.get_text(strip=True) if loc_el else "",
                "salary": price_el.get_text(strip=True) if price_el else None,
                "url": href,
                "description": "",
                "is_remote": JobNormalizer.looks_remote(title),
            }))
        return out
