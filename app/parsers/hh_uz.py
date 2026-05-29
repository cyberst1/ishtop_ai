"""HH.uz parser via the public hh.ru-compatible JSON API (area=97 = Uzbekistan)."""
from __future__ import annotations

import json
from typing import Any

from app.parsers.base import BaseParser, JobNormalizer
from app.utils.logger import logger


class HhUzParser(BaseParser):
    SOURCE = "hh_uz"
    BASE_URL = "https://api.hh.ru/vacancies"
    AREA = 97  # Uzbekistan

    async def search(self, query: str, keywords: list[str]) -> list[dict[str, Any]]:
        params = {"text": query, "area": self.AREA, "per_page": self.MAX_RESULTS}
        try:
            raw = await self._fetch(self.BASE_URL, params=params,
                                    headers={"Accept": "application/json"})
            if not raw:
                return []
            data = json.loads(raw)
        except Exception as e:
            logger.warning("hh_uz.parse_fail", extra={"err": str(e)[:200]})
            return []

        out = []
        for item in data.get("items", []):
            sal = item.get("salary") or {}
            salary = None
            if sal:
                f, t, c = sal.get("from"), sal.get("to"), sal.get("currency", "")
                if f and t:
                    salary = f"{f}-{t} {c}"
                elif f:
                    salary = f"{f}+ {c}"
                elif t:
                    salary = f"<{t} {c}"
            desc = (item.get("snippet", {}).get("requirement") or "") + " " + \
                   (item.get("snippet", {}).get("responsibility") or "")
            out.append(self.normalize({
                "title": item.get("name"),
                "company": (item.get("employer") or {}).get("name"),
                "location": (item.get("area") or {}).get("name"),
                "salary": salary,
                "url": item.get("alternate_url") or item.get("url"),
                "description": desc.strip(),
                "is_remote": JobNormalizer.looks_remote(item.get("name", "") + " " + desc),
            }))
        return out
