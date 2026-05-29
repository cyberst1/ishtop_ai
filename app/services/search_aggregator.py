"""
Aggregates jobs from multiple parsers in parallel,
runs AI keyword extraction, then de-duplicates and ranks.
"""
from __future__ import annotations

import asyncio
import hashlib
from typing import Iterable

from app.cache.jobs_cache import JobsCache
from app.parsers.registry import ParserRegistry
from app.ai.intent_guard import IntentGuard
from app.ai.job_analyzer import JobAnalyzer
from app.utils.logger import logger


def _hash_id(source: str, url: str) -> str:
    return hashlib.sha1(f"{source}::{url}".encode()).hexdigest()[:24]


class SearchAggregator:
    def __init__(self) -> None:
        self.registry = ParserRegistry()
        self.cache = JobsCache(ttl=600)

    async def search(self, query: str, role: str = "jobseeker"
                    ) -> tuple[list[dict], list[str]]:
        # 1) AI keyword extraction (with cheap fallback)
        keywords = await JobAnalyzer.extract_keywords(query)
        cache_key = f"{role}:{':'.join(sorted(keywords))}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached, keywords

        # 2) Run all parsers in parallel
        parsers = self.registry.all()
        tasks = [p.search(query, keywords) for p in parsers]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        jobs: list[dict] = []
        for r, p in zip(results, parsers):
            if isinstance(r, Exception):
                logger.warning("parser.error", extra={"source": p.SOURCE, "err": str(r)[:200]})
                continue
            for j in r:
                j.setdefault("source", p.SOURCE)
                j["id"] = _hash_id(j["source"], j["url"])
                j["keywords"] = ",".join(keywords)
                jobs.append(j)

        # 3) De-duplicate
        seen: set[str] = set()
        unique = []
        for j in jobs:
            if j["id"] in seen:
                continue
            seen.add(j["id"])
            unique.append(j)

        # 4) Rank by simple keyword score (AI scoring is on detail open)
        unique.sort(key=lambda j: _score(j, keywords), reverse=True)
        unique = unique[:20]

        self.cache.set(cache_key, unique)
        return unique, keywords


def _score(job: dict, keywords: Iterable[str]) -> int:
    text = " ".join([job.get("title", ""), job.get("description", ""),
                     job.get("location", "")]).lower()
    return sum(1 for k in keywords if k.lower() in text)
