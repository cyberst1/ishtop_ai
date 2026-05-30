"""
Generic OpenAI-compatible AI client.

Default backend is OpenRouter (https://openrouter.ai/api/v1) with
deepseek/deepseek-v4-flash:free, but any OpenAI-compatible endpoint works
because we let `settings.effective_ai_*` decide.

Handles timeouts, retries, low-temperature generations and graceful no-op
when no API key is configured.
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

    @classmethod
    def get(cls) -> Optional[AsyncOpenAI]:
        api_key = settings.effective_ai_api_key
        if not api_key:
            return None
        if cls._client is None:
            # OpenRouter recommends these headers for attribution.
            default_headers = {
                "HTTP-Referer": f"https://t.me/{settings.bot_username}",
                "X-Title": "ISH TOP AI",
            }
            cls._client = AsyncOpenAI(
                api_key=api_key,
                base_url=settings.effective_ai_base_url,
                default_headers=default_headers,
            )
        return cls._client

    @classmethod
    @retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=1, max=4))
    async def chat(cls, system: str, user: str, *, temperature: float = 0.2,
                   max_tokens: int = 600) -> str:
        client = cls.get()
        if client is None:
            return ""
        try:
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
        except asyncio.TimeoutError:
            logger.warning("ai.timeout", extra={"model": settings.effective_ai_model})
            return ""
        except Exception as e:
            logger.warning("ai.error",
                           extra={"err": str(e)[:200], "model": settings.effective_ai_model})
            return ""
