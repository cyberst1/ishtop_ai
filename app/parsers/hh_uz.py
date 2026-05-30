"""HH.uz parser via api.hh.ru (area=97 = Uzbekistan)."""
from __future__ import annotations

import json
from typing import Any

from app.parsers.base import BaseParser, JobNormalizer
from app.utils.logger import logger


class HhUzParser(BaseParser):
    SOURCE = "hh_uz"
    BASE_URL = "https://api.hh.ru/vacancies"
    AREA = 97  # Uzbekistan

    # api.hh.ru is strict about User-Agent: it must be a real-looking value
    # and *not* contain "python-requests"/aiohttp default. They block
    # cloud-IP datacenter ranges aggressively, so this may 403 on
    # Render/Railway/etc.; works fine from VPS with UZ exit IP.
    HH_HEADERS = {
        "Accept":           "application/json",
        "Accept-Language":  "uz,uz-Latn,ru;q=0.9,en;q=0.8",
        "HH-User-Agent":    "ish-top-ai/1.0 (contact: cybst_academy@telegram)",
    }

    async def search(self, query: str, keywords: list[str]) -> list[dict[str, Any]]:
        params = {
            "text": query,
            "area": self.AREA,
            "per_page": self.MAX_RESULTS,
            "order_by": "publication_time",
        }
        try:
            raw = await self._fetch(self.BASE_URL, params=params, headers=self.HH_HEADERS)
            if not raw:
                return []
            data = json.loads(raw)
        except Exception as e:
            logger.warning("hh_uz.parse_fail", extra={"err": str(e)[:200]})
            return []

        items = data.get("items") or []
        out: list[dict[str, Any]] = []
        for item in items:
            sal = item.get("salary") or {}
            salary = None
            if sal:
                f, t, c = sal.get("from"), sal.get("to"), sal.get("currency", "")
                if f and t:
                    salary = f"{f:,}-{t:,} {c}".replace(",", " ")
                elif f:
                    salary = f"{f:,}+ {c}".replace(",", " ")
                elif t:
                    salary = f"<{t:,} {c}".replace(",", " ")
            snippet = item.get("snippet") or {}
            desc = " ".join(filter(None, [
                snippet.get("requirement"), snippet.get("responsibility"),
            ]))
            out.append(self.normalize({
                "title": item.get("name"),
                "company": (item.get("employer") or {}).get("name"),
                "location": (item.get("area") or {}).get("name"),
                "salary": salary,
                "url": item.get("alternate_url") or item.get("url"),
                "description": desc.strip(),
                "is_remote": JobNormalizer.looks_remote((item.get("name") or "") + " " + desc),
            }))
        return out
