"""Indeed — public RSS feed (no API key)."""
from __future__ import annotations

from typing import Any
from urllib.parse import quote_plus
from xml.etree import ElementTree as ET

from app.parsers.base import BaseParser, JobNormalizer
from app.utils.logger import logger


class IndeedParser(BaseParser):
    SOURCE = "indeed"
    BASE_URL = "https://www.indeed.com/rss"

    async def search(self, query: str, keywords: list[str]) -> list[dict[str, Any]]:
        url = f"{self.BASE_URL}?q={quote_plus(query)}&l=Uzbekistan"
        try:
            xml = await self._fetch(url)
            if not xml:
                return []
            root = ET.fromstring(xml)
        except Exception as e:
            logger.warning("indeed.parse_fail", extra={"err": str(e)[:200]})
            return []

        out = []
        for item in root.findall(".//item")[: self.MAX_RESULTS]:
            title = (item.findtext("title") or "").strip()
            link = (item.findtext("link") or "").strip()
            desc = (item.findtext("description") or "").strip()
            if not link:
                continue
            out.append(self.normalize({
                "title": title,
                "company": "",
                "location": "Uzbekistan",
                "salary": None,
                "url": link,
                "description": desc,
                "is_remote": JobNormalizer.looks_remote(title + " " + desc),
            }))
        return out
