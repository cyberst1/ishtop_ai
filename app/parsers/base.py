"""
BaseParser — every job-board parser inherits this.

Contract:
    SOURCE: str  (unique slug used as job.source)
    async def search(self, query, keywords) -> list[dict]
        each dict must contain: title, url; may contain
        company, location, salary, description, contact, is_remote
"""
from __future__ import annotations

import asyncio
from typing import Any

import aiohttp
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.config import settings
from app.utils.logger import logger

USER_AGENT = (
    "Mozilla/5.0 (Linux; ISH-TOP-AI/1.0) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)


class BaseParser:
    SOURCE: str = "base"
    BASE_URL: str = ""
    MAX_RESULTS: int = 10

    _semaphore = asyncio.Semaphore(settings.parser_concurrency)

    async def search(self, query: str, keywords: list[str]) -> list[dict[str, Any]]:
        raise NotImplementedError

    @retry(
        reraise=True,
        retry=retry_if_exception_type(aiohttp.ClientError),
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=1, max=4),
    )
    async def _fetch(self, url: str, *, params: dict | None = None,
                     headers: dict | None = None) -> str:
        async with BaseParser._semaphore:
            timeout = aiohttp.ClientTimeout(total=settings.parser_timeout)
            hdrs = {"User-Agent": USER_AGENT, **(headers or {})}
            async with aiohttp.ClientSession(timeout=timeout, headers=hdrs) as s:
                async with s.get(url, params=params) as r:
                    if r.status >= 400:
                        logger.warning("parser.http",
                                       extra={"src": self.SOURCE, "status": r.status})
                        return ""
                    return await r.text()

    @staticmethod
    def normalize(job: dict) -> dict:
        for k in ("title", "company", "location", "salary", "description"):
            if isinstance(job.get(k), str):
                job[k] = job[k].strip()[:1000]
        return job


class JobNormalizer:
    @staticmethod
    def looks_remote(text: str) -> bool:
        t = text.lower()
        return any(w in t for w in ("remote", "uydan", "uyda", "masofadan", "udalyon"))
