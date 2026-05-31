"""
Generic OpenAI-compatible AI client (default: OpenRouter) with auto-fallback.

Key behaviour:
  • chat() tries each model in settings.ai_model_chain (primary first, then
    fallbacks) until one returns non-empty text. This keeps the AI working
    even if the configured model is slow (big reasoning model), rate-limited,
    or returns empty content.
  • chat() ALWAYS returns a string ("" only if every model fails).
  • diagnose() reports per-model results so an admin can see exactly what
    happened with /ai_test.

Free OpenRouter notes:
  • Large reasoning models (e.g. Nemotron 120B) are slow and often spend the
    token budget on hidden reasoning → empty visible content. The fallback
    chain transparently switches to a fast model in that case.
"""
from __future__ import annotations

import asyncio
from typing import Optional

from openai import AsyncOpenAI

from app.config import settings
from app.utils.logger import logger

_TIMEOUT_SECONDS = 40  # per-model timeout


class AIClient:
    _client: Optional[AsyncOpenAI] = None
    _disabled: bool = False

    @classmethod
    def get(cls) -> Optional[AsyncOpenAI]:
        if cls._disabled:
            return None
        api_key = settings.effective_ai_api_key
        if not api_key:
            return None
        if cls._client is None:
            try:
                cls._client = AsyncOpenAI(
                    api_key=api_key,
                    base_url=settings.effective_ai_base_url,
                    default_headers={
                        "HTTP-Referer": f"https://t.me/{settings.bot_username}",
                        "X-Title": "ISH TOP AI",
                    },
                )
            except Exception as e:
                cls._disabled = True
                logger.error("ai.client.init_failed", extra={"err": str(e)[:300]})
                return None
        return cls._client

    @staticmethod
    def _extract_text(resp) -> str:
        try:
            msg = resp.choices[0].message
            content = (getattr(msg, "content", None) or "").strip()
            if content:
                return content
            return (getattr(msg, "reasoning", None) or "").strip()
        except Exception:
            return ""

    @classmethod
    async def _call_model(cls, model: str, system: str, user: str, *,
                          temperature: float, max_tokens: int) -> str:
        client = cls.get()
        if client is None:
            return ""
        resp = await asyncio.wait_for(
            client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            ),
            timeout=_TIMEOUT_SECONDS,
        )
        return cls._extract_text(resp)

    @classmethod
    async def chat(cls, system: str, user: str, *, temperature: float = 0.4,
                   max_tokens: int = 900) -> str:
        """Try each model in the chain until one answers. Never raises."""
        if not settings.effective_ai_api_key:
            return ""
        for model in settings.ai_model_chain:
            try:
                text = await cls._call_model(model, system, user,
                                             temperature=temperature,
                                             max_tokens=max_tokens)
                if text:
                    return text
                logger.warning("ai.empty_response", extra={"model": model})
            except asyncio.TimeoutError:
                logger.warning("ai.timeout", extra={"model": model})
            except Exception as e:
                logger.warning("ai.error", extra={"model": model, "err": str(e)[:300]})
            # try next model in the chain
        return ""

    @classmethod
    async def diagnose(cls) -> tuple[bool, str]:
        """Test every model in the chain; report per-model results (Uzbek)."""
        if not settings.effective_ai_api_key:
            return False, "AI_API_KEY sozlanmagan (.env faylida bo'sh)."
        if cls.get() is None:
            return False, "AI klient ishga tushmadi (kutubxona/versiya muammosi)."

        lines = []
        any_ok = False
        for model in settings.ai_model_chain:
            try:
                text = await cls._call_model(
                    model, "Sen yordamchisan. Faqat 'OK' deb javob ber.",
                    "test", temperature=0.0, max_tokens=20,
                )
                if text:
                    any_ok = True
                    lines.append(f"✅ `{model}` → {text[:40]!r}")
                else:
                    lines.append(f"⚠️ `{model}` → bo'sh javob (reasoning/limit)")
            except asyncio.TimeoutError:
                lines.append(f"⏱ `{model}` → timeout ({_TIMEOUT_SECONDS}s, sekin)")
            except Exception as e:
                lines.append(f"❌ `{model}` → {_classify(str(e))}")

        header = ("✅ AI ishlayapti (kamida bitta model javob berdi)."
                  if any_ok else
                  "❌ Hech bir model javob bermadi.")
        return any_ok, header + "\n\n" + "\n".join(lines)


def _classify(detail: str) -> str:
    low = detail.lower()
    if "401" in detail or "auth" in low or "user not found" in low or "api key" in low:
        return "401 — kalit noto'g'ri/eskirgan"
    if "404" in detail or "no endpoints" in low:
        return "404 — model topilmadi / Privacy ruxsati kerak"
    if "429" in detail or "rate" in low or "quota" in low:
        return "429 — limit tugagan (free tier)"
    return f"xato: {detail[:120]}"
