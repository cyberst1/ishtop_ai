"""Jooble — official JSON API. Requires JOOBLE_API_KEY."""
from __future__ import annotations

import json
from typing import Any

import aiohttp

from app.config import settings
from app.parsers.base import BaseParser, JobNormalizer
from app.utils.logger import logger


class JoobleParser(BaseParser):
    SOURCE = "jooble"
    BASE_URL = "https://uz.jooble.org/api/{key}"

    async def search(self, query: str, keywords: list[str]) -> list[dict[str, Any]]:
        if not settings.jooble_api_key:
            return []
        url = self.BASE_URL.format(key=settings.jooble_api_key)
        payload = {"keywords": query, "location": "Uzbekistan", "page": 1}
        try:
            timeout = aiohttp.ClientTimeout(total=settings.parser_timeout)
            async with aiohttp.ClientSession(timeout=timeout) as s:
                async with s.post(url, json=payload) as r:
                    if r.status >= 400:
                        return []
                    data = await r.json()
        except Exception as e:
            logger.warning("jooble.parse_fail", extra={"err": str(e)[:200]})
            return []

        out = []
        for j in (data.get("jobs") or [])[: self.MAX_RESULTS]:
            out.append(self.normalize({
                "title": j.get("title"),
                "company": j.get("company"),
                "location": j.get("location"),
                "salary": j.get("salary"),
                "url": j.get("link"),
                "description": (j.get("snippet") or "")[:1000],
                "is_remote": JobNormalizer.looks_remote(j.get("title", "")),
            }))
        return out
