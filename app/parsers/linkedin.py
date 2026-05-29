"""
LinkedIn — public guest search HTML (no login).
Use LINKEDIN_COOKIE for better results. Lightweight + best-effort.
"""
from __future__ import annotations

from typing import Any
from urllib.parse import urlencode

from bs4 import BeautifulSoup

from app.config import settings
from app.parsers.base import BaseParser, JobNormalizer
from app.utils.logger import logger


class LinkedInParser(BaseParser):
    SOURCE = "linkedin"
    BASE_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"

    async def search(self, query: str, keywords: list[str]) -> list[dict[str, Any]]:
        params = {
            "keywords": query,
            "location": "Uzbekistan",
            "f_TPR": "r604800",  # last 7 days
            "start": 0,
        }
        url = self.BASE_URL + "?" + urlencode(params)
        headers = {}
        if settings.linkedin_cookie:
            headers["Cookie"] = settings.linkedin_cookie
        try:
            html = await self._fetch(url, headers=headers)
            if not html:
                return []
            soup = BeautifulSoup(html, "lxml")
        except Exception as e:
            logger.warning("linkedin.parse_fail", extra={"err": str(e)[:200]})
            return []

        out: list[dict[str, Any]] = []
        cards = soup.select("div.base-card")[: self.MAX_RESULTS]
        for c in cards:
            t = c.select_one(".base-search-card__title")
            comp = c.select_one(".base-search-card__subtitle")
            loc = c.select_one(".job-search-card__location")
            link_el = c.select_one("a.base-card__full-link")
            href = link_el.get("href") if link_el else None
            if not href:
                continue
            title = t.get_text(strip=True) if t else ""
            out.append(self.normalize({
                "title": title,
                "company": comp.get_text(strip=True) if comp else "",
                "location": loc.get_text(strip=True) if loc else "",
                "salary": None,
                "url": href.split("?")[0],
                "description": "",
                "is_remote": JobNormalizer.looks_remote(title),
            }))
        return out
