"""ish-kerak.uz HTML parser — Bootstrap card listing."""
from __future__ import annotations

from typing import Any
from urllib.parse import quote_plus

from bs4 import BeautifulSoup

from app.parsers.base import BaseParser, JobNormalizer
from app.utils.logger import logger


class IshKerakParser(BaseParser):
    SOURCE = "ishkerak_uz"
    BASE_URL = "https://ish-kerak.uz/ishlar"

    async def search(self, query: str, keywords: list[str]) -> list[dict[str, Any]]:
        params = {"q": query}
        try:
            html = await self._fetch(self.BASE_URL, params=params)
            if not html:
                return []
            soup = BeautifulSoup(html, "lxml")
        except Exception as e:
            logger.warning("ishkerak.parse_fail", extra={"err": str(e)[:200]})
            return []

        cards = soup.select("div.card.zoom > div.card-body")[: self.MAX_RESULTS]
        out: list[dict[str, Any]] = []
        for c in cards:
            link_el = c.select_one("b > a[href]")
            if not link_el:
                continue
            href = link_el.get("href", "")
            if href.startswith("/"):
                href = "https://ish-kerak.uz" + href
            title = link_el.get_text(strip=True)

            salary_el = c.select_one("b.text-danger")
            salary = None
            if salary_el:
                raw = salary_el.get_text(strip=True).replace("/", "").strip()
                if raw.replace(" ", "").isdigit():
                    salary = f"{int(raw.replace(' ', '')):,} UZS".replace(",", " ")
                else:
                    salary = raw

            loc_el = c.select_one("p.card-text > small.text-muted")
            location = ""
            if loc_el:
                location = loc_el.get_text(strip=True).lstrip("⛳ ").strip()

            out.append(self.normalize({
                "title": title,
                "company": "",
                "location": location,
                "salary": salary,
                "url": href,
                "description": "",
                "is_remote": JobNormalizer.looks_remote(title),
            }))
        return out
