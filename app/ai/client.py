"""
Generic OpenAI-compatible AI client.

Default backend is OpenRouter (https://openrouter.ai/api/v1) with
deepseek/deepseek-v4-flash:free, but any OpenAI-compatible endpoint works
because we let `settings.effective_ai_*` decide.

BULLETPROOF: every entry point catches all exceptions. `chat()` ALWAYS returns
a string (empty on any failure). Initialisation failures (e.g. version
mismatch between openai and httpx) are logged once and the client is marked
unusable so subsequent calls return "" without retrying.
"""
from __future__ import annotations

import asyncio
from typing import Optional

from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import settings
from app.utils.logger import logger


class AIClient:
    _client: Optional[AsyncOpenAI] = None
    _disabled: bool = False  # set to True after a fatal init error

    @classmethod
    def get(cls) -> Optional[AsyncOpenAI]:
        if cls._disabled:
            return None
        api_key = settings.effective_ai_api_key
        if not api_key:
            return None
        if cls._client is None:
            try:
                default_headers = {
                    "HTTP-Referer": f"https://t.me/{settings.bot_username}",
                    "X-Title": "ISH TOP AI",
                }
                cls._client = AsyncOpenAI(
                    api_key=api_key,
                    base_url=settings.effective_ai_base_url,
                    default_headers=default_headers,
                )
            except Exception as e:
                # e.g. openai/httpx version mismatch — never crash the bot
                cls._disabled = True
                logger.error(
                    "ai.client.init_failed",
                    extra={"err": str(e)[:200]},
                )
                return None
        return cls._client

    @classmethod
    @retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=1, max=4))
    async def _do_chat(cls, system: str, user: str, *,
                       temperature: float, max_tokens: int) -> str:
        client = cls.get()
        if client is None:
            return ""
        resp = await asyncio.wait_for(
            client.chat.completions.create(
                model=settings.effective_ai_model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            ),
            timeout=20,
        )
        return (resp.choices[0].message.content or "").strip()

    @classmethod
    async def chat(cls, system: str, user: str, *, temperature: float = 0.2,
                   max_tokens: int = 600) -> str:
        """Public entry. NEVER raises — returns "" on any failure."""
        try:
            return await cls._do_chat(system, user, temperature=temperature,
                                      max_tokens=max_tokens)
        except asyncio.TimeoutError:
            logger.warning("ai.timeout", extra={"model": settings.effective_ai_model})
        except Exception as e:
            logger.warning(
                "ai.error",
                extra={"err": str(e)[:200], "model": settings.effective_ai_model},
            )
        return ""
