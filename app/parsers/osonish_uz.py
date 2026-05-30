"""osonish.uz parser — public JSON API."""
from __future__ import annotations

import json
from typing import Any

from app.parsers.base import BaseParser, JobNormalizer
from app.utils.logger import logger


class OsonishUzParser(BaseParser):
    SOURCE = "osonish_uz"
    BASE_URL = "https://osonish.uz/api/v1/vacancies"

    async def search(self, query: str, keywords: list[str]) -> list[dict[str, Any]]:
        params = {"q": query, "page": 1}
        try:
            raw = await self._fetch(self.BASE_URL, params=params,
                                    headers={"Accept": "application/json"})
            if not raw:
                return []
            payload = json.loads(raw)
        except Exception as e:
            logger.warning("osonish.parse_fail", extra={"err": str(e)[:200]})
            return []

        items = (payload.get("data") or {}).get("data") or []
        out: list[dict[str, Any]] = []
        for it in items[: self.MAX_RESULTS]:
            title = it.get("title") or ""
            min_s = it.get("min_salary")
            max_s = it.get("max_salary")
            salary = None
            if min_s and max_s:
                salary = f"{min_s:,}-{max_s:,} UZS".replace(",", " ")
            elif min_s:
                salary = f"{min_s:,}+ UZS".replace(",", " ")
            elif max_s:
                salary = f"<{max_s:,} UZS".replace(",", " ")

            company = ""
            if it.get("company"):
                company = (it["company"].get("name") or "").strip()
            location = it.get("address") or ""
            if it.get("filial") and it["filial"].get("address"):
                location = it["filial"]["address"]

            url = f"https://osonish.uz/vacancies/{it.get('id')}"
            out.append(self.normalize({
                "title": title,
                "company": company,
                "location": location,
                "salary": salary,
                "url": url,
                "description": "",
                "is_remote": JobNormalizer.looks_remote(title),
            }))
        return out
