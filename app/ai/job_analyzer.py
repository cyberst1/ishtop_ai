"""
Convert free-form Uzbek/Russian/English queries to a search-friendly
keyword bag.  Works fully offline — LLM is consulted only as a bonus.

Examples:
  "Telegram bot yasab beraman"      → ["telegram", "bot", "developer", "freelance"]
  "Web sayt qilib beraman"          → ["website", "developer", "freelance"]
  "Toshkentda kuryer kerak"         → ["courier", "delivery", "toshkent"]
  "Uyda ishlasam bo'ladi"           → ["remote"]
  "Junior python developer"          → ["junior", "python", "developer"]
"""
from __future__ import annotations

import json
import re

from app.ai.client import AIClient
from app.ai.prompts import KEYWORDS_EXTRACTOR, JOB_ANALYZER

# ────────────────────────── synonym lexicon ──────────────────────────
# Maps Uzbek / Russian / colloquial words to canonical English search terms.
_SYNONYMS = {
    # === remote / location ===
    "uyda":        "remote",
    "uydan":       "remote",
    "masofadan":   "remote",
    "udalyon":     "remote",
    "udalyonno":   "remote",
    "online":      "remote",
    "ofis":        "office",

    # === verbs that imply "I do/make X" → developer/freelance ===
    "yasab":       "developer",
    "yasayman":    "developer",
    "yarataman":   "developer",
    "qilaman":     "developer",
    "qilib":       "developer",
    "tuzaman":     "developer",
    "tuzib":       "developer",
    "ishlab":      "developer",
    "ishlayman":   "developer",
    "chiqaraman":  "developer",
    "yozib":       "developer",
    "yozaman":     "developer",
    "kerak":       "",   # ignore
    "beraman":     "freelance",   # "qilib beraman" → freelance offer
    "berasizmi":   "freelance",

    # === IT specialties ===
    "dasturchi":     "developer",
    "muhandis":      "engineer",
    "dizayner":      "designer",
    "dizayn":        "designer",
    "logo":          "logo designer",
    "grafik":        "graphic designer",
    "frontend":      "frontend",
    "backend":       "backend",
    "fullstack":     "fullstack",
    "mobile":        "mobile developer",
    "android":       "android developer",
    "ios":           "ios developer",
    "tester":        "qa tester",
    "qa":            "qa tester",
    "devops":        "devops",
    "data":          "data analyst",
    "analitik":      "analyst",
    "boshqaruvchi":  "manager",
    "menejer":       "manager",
    "manager":       "manager",

    # === languages / frameworks ===
    "python":      "python",
    "java":        "java",
    "javascript":  "javascript",
    "js":          "javascript",
    "php":         "php",
    "ruby":        "ruby",
    "go":          "golang",
    "golang":      "golang",
    "kotlin":      "kotlin",
    "swift":       "swift",
    "react":       "react",
    "vue":         "vue",
    "angular":     "angular",
    "node":        "nodejs",
    "django":      "django",
    "flask":       "flask",
    "fastapi":     "fastapi",
    "spring":      "spring",
    "laravel":     "laravel",

    # === product types ===
    "sayt":         "website",
    "vebsayt":      "website",
    "veb":          "web",
    "web":          "web",
    "bot":          "bot",
    "telegram":     "telegram",
    "chatbot":      "chatbot",
    "dastur":       "software",
    "ilova":        "app",
    "mobil":        "mobile",
    "kompyuter":    "computer",
    "ai":           "ai",
    "sun":          "ai",   # sun'iy intellekt
    "intellekt":    "ai",
    "neyron":       "machine learning",

    # === marketing / sales ===
    "smm":         "smm",
    "marketing":   "marketing",
    "marketolog":  "marketing manager",
    "reklama":     "advertising",
    "savdo":       "sales",
    "sotuvchi":    "sales",
    "savdogar":    "sales",

    # === blue-collar / services ===
    "kuryer":      "courier",
    "yetkazib":    "delivery",
    "yetkazish":   "delivery",
    "haydovchi":   "driver",
    "shofyor":     "driver",
    "ovqat":       "food",
    "oshpaz":      "cook",
    "ofitsiant":   "waiter",
    "kassir":      "cashier",
    "ishchi":      "worker",
    "xodim":       "employee",
    "buxgalter":   "accountant",
    "huquqshunos": "lawyer",
    "advokat":     "lawyer",
    "shifokor":    "doctor",
    "hamshira":    "nurse",
    "tarbiyachi":  "kindergarten teacher",
    "o'qituvchi":  "teacher",
    "oqituvchi":   "teacher",

    # === levels ===
    "junior":      "junior",
    "middle":      "middle",
    "senior":      "senior",
    "stajirovka":  "internship",
    "amaliyot":    "internship",
    "tajriba":     "experience",

    # === Uzbek cities ===
    "toshkent":    "tashkent",
    "samarqand":   "samarkand",
    "buxoro":      "bukhara",
    "andijon":     "andijan",
    "namangan":    "namangan",
    "fargona":     "fergana",
    "navoi":       "navoi",
    "qarshi":      "qarshi",
    "termiz":      "termez",
    "nukus":       "nukus",
    "jizzax":      "jizzakh",
    "guliston":    "guliston",
    "xorazm":      "khorezm",
}

_STOPWORDS = {
    "men", "siz", "sen", "biz", "uning", "bir", "shu", "bu",
    "uchun", "bo'lsa", "boladi", "ko'p", "ham", "lekin", "agar",
    "the", "and", "or", "of", "to", "in", "on", "at", "is", "are",
    "ya", "ne", "i", "v", "na", "po", "s",
    "deb", "yoki", "shunday", "qanday", "qaysi",
}


# Uzbek case suffixes — strip from the end so "toshkentda" → "toshkent"
_UZ_SUFFIXES = ("ningdagi", "lardagi", "ningda", "ning", "lar", "dan",
                "ga", "da", "ni", "ham")


def _stem(w: str) -> str:
    for suf in _UZ_SUFFIXES:
        if len(w) > len(suf) + 2 and w.endswith(suf):
            return w[:-len(suf)]
    return w


def _expand(words: list[str]) -> list[str]:
    """Apply synonym expansion + remove stopwords + dedupe."""
    out: list[str] = []
    seen: set[str] = set()
    for w in words:
        w = w.strip()
        if not w or w in _STOPWORDS:
            continue
        # Try synonyms; if none, try the stemmed form; else keep word as-is
        if w in _SYNONYMS:
            mapped = _SYNONYMS[w]
        else:
            stem = _stem(w)
            mapped = _SYNONYMS.get(stem, stem)
        if not mapped:
            continue
        # multi-token synonym (e.g. "logo designer")
        for token in mapped.split():
            if token not in seen:
                seen.add(token)
                out.append(token)
    return out


class JobAnalyzer:
    @staticmethod
    async def extract_keywords(query: str) -> list[str]:
        # 1) Tokenize: keep apostrophes (uzbek o', g')
        words = [w.lower() for w in re.split(r"[^\wʻ']+", query) if len(w) >= 2]
        baseline = _expand(words)

        # If we already have decent keywords, return them.
        if len(baseline) >= 2:
            return baseline[:12]

        # 2) Otherwise also consult the LLM (cheap + quick) when available
        raw = await AIClient.chat(KEYWORDS_EXTRACTOR, query, temperature=0.0, max_tokens=200)
        if not raw:
            return baseline[:12] or words[:8]
        try:
            data = json.loads(raw)
            kws = data.get("keywords") or []
            if not isinstance(kws, list):
                return baseline[:12] or words[:8]
            merged = list(dict.fromkeys([*baseline, *[str(k).lower() for k in kws]]))
            return merged[:12]
        except (ValueError, TypeError):
            return baseline[:12] or words[:8]

    @staticmethod
    async def summarize(job_text: str) -> str:
        return await AIClient.chat(JOB_ANALYZER, job_text[:4000],
                                   temperature=0.3, max_tokens=300)
