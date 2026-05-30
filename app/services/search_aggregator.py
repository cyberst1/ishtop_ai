"""
Aggregates jobs from 6 parsers in parallel.

Pipeline:
  1. AI keyword extraction (with offline fallback)
  2. Build a *parser-friendly* query from the keywords (top 3-4)
     so phrases like "Telegram bot yasab beraman" become "telegram bot developer"
  3. Run all parsers in parallel against that effective query
  4. De-duplicate, rank by keyword score, return top 20
"""
from __future__ import annotations

import asyncio
import hashlib
from typing import Iterable

from app.ai.intent_guard import IntentGuard
from app.ai.job_analyzer import JobAnalyzer
from app.cache.jobs_cache import JobsCache
from app.parsers.registry import ParserRegistry
from app.utils.logger import logger


def _hash_id(source: str, url: str) -> str:
    return hashlib.sha1(f"{source}::{url}".encode()).hexdigest()[:24]


def _build_effective_query(original: str, keywords: list[str]) -> str:
    """
    Build a query string parsers can actually use.

    If the user typed plain keywords (≤ 4 words and they all match the
    extracted keywords), keep the original.  Otherwise, build a query
    from the top 4 keywords — this turns natural-language phrasing into
    something HH/OLX can actually search.
    """
    words = original.split()
    if len(words) <= 4 and all(w.lower() in " ".join(keywords).lower() for w in words):
        return original.strip()
    # fall back to the top keywords (they're already english/canonical)
    top = keywords[:4] if keywords else words[:3]
    return " ".join(top) or original.strip()


class SearchAggregator:
    def __init__(self) -> None:
        self.registry = ParserRegistry()
        self.cache = JobsCache(ttl=600)

    async def search(self, query: str, role: str = "jobseeker"
                    ) -> tuple[list[dict], list[str]]:
        # 1. Keywords
        keywords = await JobAnalyzer.extract_keywords(query)

        # 2. Effective parser query
        eff_query = _build_effective_query(query, keywords)

        cache_key = f"{role}:{eff_query}:{':'.join(sorted(keywords))}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached, keywords

        logger.info(
            "search.aggregator.run",
            extra={"original": query[:60], "effective": eff_query[:60],
                   "keywords": keywords[:6]},
        )

        # 3. Parallel parser run
        parsers = self.registry.all()
        tasks = [p.search(eff_query, keywords) for p in parsers]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        jobs: list[dict] = []
        for r, p in zip(results, parsers):
            if isinstance(r, Exception):
                logger.warning("parser.error",
                               extra={"source": p.SOURCE, "err": str(r)[:200]})
                continue
            for j in r:
                j.setdefault("source", p.SOURCE)
                j["id"] = _hash_id(j["source"], j["url"])
                j["keywords"] = ",".join(keywords)
                jobs.append(j)

        # 4. De-duplicate
        seen: set[str] = set()
        unique = []
        for j in jobs:
            if j["id"] in seen:
                continue
            seen.add(j["id"])
            unique.append(j)

        # 5. Rank by keyword overlap
        unique.sort(key=lambda j: _score(j, keywords), reverse=True)
        unique = unique[:20]

        self.cache.set(cache_key, unique)
        return unique, keywords


def _score(job: dict, keywords: Iterable[str]) -> int:
    text = " ".join([
        job.get("title", ""), job.get("description", ""), job.get("location", ""),
    ]).lower()
    return sum(1 for k in keywords if k.lower() in text)
