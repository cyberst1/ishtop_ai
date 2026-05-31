"""
Generic OpenAI-compatible AI client (default: OpenRouter).

BULLETPROOF: `chat()` ALWAYS returns a string ("" on any failure).
`diagnose()` is a debug helper that returns the REAL error/detail so an
admin can see exactly why the AI is silent.

Notes for free OpenRouter models:
  • Large reasoning models (e.g. Nemotron 120B) are SLOW and spend tokens on
    hidden reasoning — if max_tokens is small the visible content can come back
    empty. We therefore use a generous timeout and pull text from both the
    `content` and (if present) `reasoning` fields.
  • Free tiers are rate-limited (HTTP 429) and some require a privacy opt-in
    (HTTP 404 'No endpoints found'). diagnose() surfaces these clearly.
"""
from __future__ import annotations

import asyncio
from typing import Optional

from openai import AsyncOpenAI

from app.config import settings
from app.utils.logger import logger

_TIMEOUT_SECONDS = 45  # big reasoning models can be slow on the free tier


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
        """Pull visible text from a completion, tolerating reasoning models."""
        try:
            choice = resp.choices[0]
            msg = choice.message
            content = (getattr(msg, "content", None) or "").strip()
            if content:
                return content
            # some reasoning models expose text under .reasoning
            reasoning = (getattr(msg, "reasoning", None) or "").strip()
            return reasoning
        except Exception:
            return ""

    @classmethod
    async def _create(cls, system: str, user: str, *, temperature: float,
                      max_tokens: int):
        client = cls.get()
        if client is None:
            return None
        return await asyncio.wait_for(
            client.chat.completions.create(
                model=settings.effective_ai_model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            ),
            timeout=_TIMEOUT_SECONDS,
        )

    @classmethod
    async def chat(cls, system: str, user: str, *, temperature: float = 0.2,
                   max_tokens: int = 900) -> str:
        """Public entry. NEVER raises — returns "" on any failure."""
        for attempt in (1, 2):
            try:
                resp = await cls._create(system, user, temperature=temperature,
                                         max_tokens=max_tokens)
                if resp is None:
                    return ""
                text = cls._extract_text(resp)
                if text:
                    return text
                logger.warning("ai.empty_response",
                               extra={"model": settings.effective_ai_model,
                                      "attempt": attempt})
            except asyncio.TimeoutError:
                logger.warning("ai.timeout",
                               extra={"model": settings.effective_ai_model,
                                      "attempt": attempt})
            except Exception as e:
                logger.warning("ai.error",
                               extra={"err": str(e)[:300],
                                      "model": settings.effective_ai_model,
                                      "attempt": attempt})
                break  # don't retry hard errors (auth/model/quota)
        return ""

    @classmethod
    async def diagnose(cls) -> tuple[bool, str]:
        """
        Run a minimal test call and return (ok, human-readable detail).
        Used by the admin /ai_test command.
        """
        if not settings.effective_ai_api_key:
            return False, "AI_API_KEY sozlanmagan (.env faylida bo'sh)."
        client = cls.get()
        if client is None:
            return False, "AI klient ishga tushmadi (kutubxona/versiya muammosi)."
        try:
            resp = await cls._create(
                "Sen yordamchisan. Faqat 'OK' deb javob ber.",
                "test", temperature=0.0, max_tokens=20,
            )
            text = cls._extract_text(resp)
            if text:
                return True, f"✅ Ishlayapti. Model javobi: {text[:80]!r}"
            return False, (
                "Model bo'sh javob qaytardi. Sabab: ehtimol reasoning modeli "
                "max_tokens'ni tugatdi yoki model vaqtincha band. "
                "Tezroq model tavsiya etiladi (masalan deepseek/deepseek-v4-flash:free)."
            )
        except asyncio.TimeoutError:
            return False, (
                f"⏱ Timeout ({_TIMEOUT_SECONDS}s). Model juda sekin — "
                "tezroq model tanlang (deepseek/deepseek-v4-flash:free)."
            )
        except Exception as e:
            detail = str(e)
            # Make common OpenRouter errors human-friendly
            low = detail.lower()
            if "401" in detail or "auth" in low or "api key" in low:
                hint = "API kalit noto'g'ri yoki eskirgan."
            elif "404" in detail or "no endpoints" in low:
                hint = ("Model topilmadi yoki ruxsat yo'q. OpenRouter Privacy "
                        "sozlamalarida free modellarga ruxsat bering yoki "
                        "boshqa model tanlang.")
            elif "429" in detail or "rate" in low or "quota" in low:
                hint = "Limit tugagan (free tier kunlik cheklov). Keyinroq urinib ko'ring."
            else:
                hint = "Noma'lum xato."
            return False, f"❌ {hint}\n\nTexnik: {detail[:300]}"
