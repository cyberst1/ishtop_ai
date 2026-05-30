"""
Live, admin-editable runtime configuration.

Falls back to the static `settings` (loaded from .env) when a key isn't set
in the DB. All values are exposed as plain attributes so callers don't need
to know whether the value came from DB or env.

Editable keys:
  premium_price          int  — Premium tariff (so'm)
  premium_plus_price     int  — Premium+ tariff (so'm)
  search_cost            float — coin per search
  signup_gift_coins      float — gift on first /start
  free_daily_searches    int   — daily search limit (free plan)
  bonus_channel_reward   float — coin reward for joining a bonus channel
  referral_first_bonus   float — coin for the first invited friend
  referral_next_bonus    float — coin for each next invited friend
"""
from __future__ import annotations

import asyncio

from app.config import settings
from app.database.repositories import AppSettingsRepo

# Schema of editable keys — defaults pulled from `settings`
EDITABLE_KEYS: dict[str, type] = {
    "premium_price":         int,
    "premium_plus_price":    int,
    "search_cost":           float,
    "signup_gift_coins":     float,
    "free_daily_searches":   int,
    "bonus_channel_reward":  float,
    "referral_first_bonus":  float,
    "referral_next_bonus":   float,
}

# Human-readable labels (Uzbek) for the admin price editor
LABELS: dict[str, str] = {
    "premium_price":         "⭐ Premium narxi (so'm)",
    "premium_plus_price":    "💎 Premium+ narxi (so'm)",
    "search_cost":           "🪙 Qidiruv narxi (coin)",
    "signup_gift_coins":     "🎁 Ro'yxatdan o'tish sovg'asi (coin)",
    "free_daily_searches":   "📅 Free kunlik limit (qidiruv)",
    "bonus_channel_reward":  "🎁 Bonus kanal mukofoti (coin)",
    "referral_first_bonus":  "👥 1-do'st mukofoti (coin)",
    "referral_next_bonus":   "👥 Keyingi do'stlar mukofoti (coin)",
}


class RuntimeConfig:
    """Singleton runtime config — call `refresh()` on startup, then use attrs."""

    _instance: "RuntimeConfig | None" = None
    _lock = asyncio.Lock()

    def __init__(self) -> None:
        # initialize from env defaults
        for key, _typ in EDITABLE_KEYS.items():
            setattr(self, key, getattr(settings, key))

    @classmethod
    def get(cls) -> "RuntimeConfig":
        if cls._instance is None:
            cls._instance = RuntimeConfig()
        return cls._instance

    async def refresh(self) -> None:
        """Reload all editable keys from the DB on top of env defaults."""
        async with self._lock:
            data = await AppSettingsRepo.all()
            for key, typ in EDITABLE_KEYS.items():
                if key in data:
                    try:
                        setattr(self, key, typ(data[key]))
                    except (ValueError, TypeError):
                        # bad value → keep env default
                        setattr(self, key, getattr(settings, key))
                else:
                    setattr(self, key, getattr(settings, key))

    async def update(self, key: str, value, admin_id: int | None = None) -> None:
        if key not in EDITABLE_KEYS:
            raise KeyError(f"unknown setting: {key}")
        typ = EDITABLE_KEYS[key]
        # validate cast
        casted = typ(value)
        await AppSettingsRepo.set(key, str(casted), admin_id=admin_id)
        async with self._lock:
            setattr(self, key, casted)

    def label(self, key: str) -> str:
        return LABELS.get(key, key)


# Global accessor — import this everywhere prices/limits are used
runtime = RuntimeConfig.get()
