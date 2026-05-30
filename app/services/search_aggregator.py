"""
Aggregates jobs from multiple Uzbekistan-focused parsers in parallel
AND filters out irrelevant results.

Pipeline:
  1. AI keyword extraction
  2. Build effective parser query
  3. Run all parsers concurrently
  4. SCORE every result by keyword overlap with original-query + keywords
  5. KEEP only results with score >= MIN_SCORE
     (this drops featured/sponsored listings that the source returns even
      when nothing actually matches the query)
  6. De-duplicate, rank by score (desc), top 20
  7. Cache only non-empty results for 10 min
"""
from __future__ import annotations

import asyncio
import hashlib
import re
from typing import Iterable

from app.ai.job_analyzer import JobAnalyzer
from app.cache.jobs_cache import JobsCache
from app.parsers.registry import ParserRegistry
from app.utils.logger import logger

# A result must contain at least this many of the query's keywords/tokens
# in title+description+location.  Higher → stricter → fewer false positives.
MIN_SCORE = 1


def _hash_id(source: str, url: str) -> str:
    return hashlib.sha1(f"{source}::{url}".encode()).hexdigest()[:24]


def _build_effective_query(original: str, keywords: list[str]) -> str:
    words = original.split()
    if len(words) <= 3 and all(
        w.lower() in " ".join(keywords).lower() for w in words
    ):
        return original.strip()
    if not keywords:
        return original.strip()
    return " ".join(keywords[:3])


def _score(job: dict, terms: Iterable[str]) -> int:
    text = " ".join([
        job.get("title") or "",
        job.get("description") or "",
        job.get("location") or "",
        job.get("company") or "",
    ]).lower()
    return sum(1 for t in terms if t.lower() in text)


def _query_tokens(query: str) -> list[str]:
    """Words from the original user query that are 3+ chars."""
    return [w.lower() for w in re.split(r"[^\wʻ']+", query) if len(w) >= 3]


class SearchAggregator:
    def __init__(self) -> None:
        self.registry = ParserRegistry()
        self.cache = JobsCache(ttl=600)

    async def search(self, query: str, role: str = "jobseeker"
                    ) -> tuple[list[dict], list[str]]:
        keywords = await JobAnalyzer.extract_keywords(query)
        eff_query = _build_effective_query(query, keywords)

        cache_key = f"{role}:{eff_query}:{':'.join(sorted(keywords))}"
        cached = self.cache.get(cache_key)
        if cached:
            logger.info("search.cache_hit", extra={"key": cache_key[:60]})
            return cached, keywords

        logger.info(
            "search.aggregator.run",
            extra={"original": query[:60], "effective": eff_query[:60],
                   "keywords": keywords[:8]},
        )

        parsers = self.registry.all()
        tasks = [p.search(eff_query, keywords) for p in parsers]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Combine score-evaluation terms: extracted keywords + meaningful
        # tokens from the user's original query.  This catches cases where
        # the LLM/synonym layer dropped a token that's still useful for
        # matching (e.g. proper nouns).
        score_terms = list(dict.fromkeys(keywords + _query_tokens(query)))

        # Collect with scores
        scored: list[tuple[int, dict]] = []
        per_source: dict[str, int] = {}
        for r, p in zip(results, parsers):
            if isinstance(r, Exception):
                logger.warning("parser.error",
                               extra={"source": p.SOURCE, "err": str(r)[:200]})
                per_source[p.SOURCE] = -1
                continue
            kept = 0
            for j in r:
                j.setdefault("source", p.SOURCE)
                j["id"] = _hash_id(j["source"], j["url"])
                j["keywords"] = ",".join(keywords)
                s = _score(j, score_terms)
                if s >= MIN_SCORE:
                    scored.append((s, j))
                    kept += 1
            per_source[p.SOURCE] = f"{kept}/{len(r)}"

        logger.info("search.parsers", extra={"per_source": per_source})

        # De-duplicate by id, keeping highest-scored copy
        best: dict[str, tuple[int, dict]] = {}
        for s, j in scored:
            prev = best.get(j["id"])
            if prev is None or prev[0] < s:
                best[j["id"]] = (s, j)

        unique = sorted(best.values(), key=lambda kv: kv[0], reverse=True)
        unique = [j for _s, j in unique][:20]

        if unique:
            self.cache.set(cache_key, unique)
        return unique, keywords
