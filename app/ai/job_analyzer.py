"""Extract keywords / synonyms / level / remote intent from a free-text query."""
from __future__ import annotations

import json
import re

from app.ai.client import AIClient
from app.ai.prompts import KEYWORDS_EXTRACTOR, JOB_ANALYZER

_SYNONYMS = {
    "uydan": "remote", "uyda": "remote", "masofadan": "remote",
    "udalyon": "remote", "online": "remote",
    "dasturchi": "developer", "muhandis": "engineer",
    "dizayner": "designer", "marketolog": "marketing",
    "frontend": "frontend", "backend": "backend", "fullstack": "fullstack",
    "smm": "smm", "menejer": "manager", "manager": "manager",
}


class JobAnalyzer:
    @staticmethod
    async def extract_keywords(query: str) -> list[str]:
        # Fast deterministic baseline
        words = [w.lower() for w in re.split(r"\W+", query) if len(w) > 2]
        baseline = []
        seen = set()
        for w in words:
            mapped = _SYNONYMS.get(w, w)
            if mapped not in seen:
                seen.add(mapped)
                baseline.append(mapped)
        if not baseline:
            return []

        raw = await AIClient.chat(KEYWORDS_EXTRACTOR, query, temperature=0.0, max_tokens=200)
        if not raw:
            return baseline[:10]
        try:
            data = json.loads(raw)
            kws = data.get("keywords") or []
            if not isinstance(kws, list):
                return baseline[:10]
            merged = list(dict.fromkeys([*baseline, *[str(k).lower() for k in kws]]))
            return merged[:12]
        except (ValueError, TypeError):
            return baseline[:10]

    @staticmethod
    async def summarize(job_text: str) -> str:
        return await AIClient.chat(JOB_ANALYZER, job_text[:4000], temperature=0.3, max_tokens=300)
