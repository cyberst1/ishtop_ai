"""Salary range estimation in UZS."""
from __future__ import annotations

import json

from app.ai.client import AIClient
from app.ai.prompts import SALARY_ESTIMATOR


class SalaryEstimator:
    @staticmethod
    async def estimate(role_text: str) -> dict | None:
        raw = await AIClient.chat(SALARY_ESTIMATOR, role_text[:2000],
                                  temperature=0.0, max_tokens=120)
        if not raw:
            return None
        try:
            return json.loads(raw)
        except (ValueError, TypeError):
            return None
