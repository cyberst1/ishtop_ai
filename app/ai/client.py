"""
NVIDIA NIM client (OpenAI-compatible).
Handles timeouts, retries, low-temperature generations, and graceful fallback.
"""
from __future__ import annotations

import asyncio
from typing import Any

from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import settings
from app.utils.logger import logger


class AIClient:
    _client: AsyncOpenAI | None = None

    @classmethod
    def get(cls) -> AsyncOpenAI:
        if cls._client is None:
            cls._client = AsyncOpenAI(
                api_key=settings.nvidia_api_key or "missing",
                base_url=settings.nvidia_base_url,
            )
        return cls._client

    @classmethod
    @retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=1, max=4))
    async def chat(cls, system: str, user: str, *, temperature: float = 0.2,
                   max_tokens: int = 600) -> str:
        if not settings.nvidia_api_key:
            return ""  # graceful no-op when key missing
        try:
            resp = await asyncio.wait_for(
                cls.get().chat.completions.create(
                    model=settings.nvidia_model,
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
            logger.warning("ai.timeout")
            return ""
        except Exception as e:
            logger.warning("ai.error", extra={"err": str(e)[:200]})
            return ""
