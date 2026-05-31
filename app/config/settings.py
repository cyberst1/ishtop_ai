"""
Centralized configuration via pydantic-settings.

IMPORTANT: We load .env *manually* with interpolate=False so that the
`$` characters inside bcrypt hashes (e.g. `$2b$12$...`) are preserved verbatim.
"""
from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# ---- Pre-load .env without interpolation (preserves $ in bcrypt hash) ----
_ENV_PATH = Path(".env")
if _ENV_PATH.exists():
    load_dotenv(_ENV_PATH, override=False, interpolate=False)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=None,
        case_sensitive=False,
        extra="ignore",
    )

    # ---- Telegram ----
    bot_token: str = Field(..., min_length=20)
    bot_username: str = "ish_top_ai_bot"

    # ---- Admin ----
    admin_ids_raw: str = Field(default="", alias="ADMIN_IDS")
    admin_password: str = ""
    admin_password_hash: str = ""
    admin_session_ttl_minutes: int = 30

    # ---- AI (OpenRouter — OpenAI-compatible) ----
    # Primary (new) keys
    ai_api_key: str = ""
    ai_base_url: str = "https://openrouter.ai/api/v1"
    ai_model: str = "deepseek/deepseek-v4-flash:free"
    # Legacy NVIDIA aliases — still read from .env if present
    nvidia_api_key: str = ""
    nvidia_base_url: str = ""
    nvidia_model: str = ""

    # ---- Database ----
    database_path: str = "data/ish_top_ai.db"

    # ---- Mode ----
    mode: str = "polling"
    webhook_url: str = ""
    webhook_secret: str = ""
    webapp_host: str = "0.0.0.0"
    webapp_port: int = 8080

    # ---- Security ----
    hmac_secret: str = "change_me_now_please_generate_random"
    rate_limit_per_min: int = 20

    # ---- Logging ----
    log_level: str = "INFO"
    log_dir: str = "data/logs"

    # ---- Parsers ----
    parser_timeout: int = 15
    parser_concurrency: int = 4
    jooble_api_key: str = ""
    linkedin_cookie: str = ""

    # ---- Telegram channels parser ----
    tg_api_id: Optional[int] = None
    tg_api_hash: str = ""

    # ---- Economy constants ----
    signup_gift_coins: float = 4.0
    search_cost: float = 2.0
    job_unlock_cost: float = 0.0
    referral_first_bonus: float = 2.0
    referral_next_bonus: float = 1.0
    bonus_channel_reward: float = 0.5
    free_daily_searches: int = 3

    # ---- Pricing (so'm) ----
    premium_price: int = 6_000
    premium_plus_price: int = 14_900
    premium_plus_bonus_coins: float = 30.0   # bonus coins granted with Premium+
    plan_duration_days: int = 14             # all paid plans last 14 days

    # ---- Branding / Support ----
    support_username: str = "cybst_academy"

    # ---- Payment ----
    payment_card_number: str = "8600 4906 7728 0114"
    payment_card_owner: str = "Cyber ST Academy"

    # -------------------- validators --------------------

    @field_validator("tg_api_id", mode="before")
    @classmethod
    def _parse_tg_api_id(cls, v):
        if v is None or v == "":
            return None
        return v

    @field_validator(
        "admin_session_ttl_minutes", "rate_limit_per_min",
        "webapp_port", "parser_timeout", "parser_concurrency",
        mode="before",
    )
    @classmethod
    def _empty_str_to_default(cls, v, info):
        if v is None or v == "":
            return cls.model_fields[info.field_name].default
        return v

    # -------------------- properties --------------------

    @property
    def admin_ids(self) -> List[int]:
        raw = (self.admin_ids_raw or "").strip()
        if not raw:
            return []
        out: List[int] = []
        for chunk in raw.split(","):
            chunk = chunk.strip()
            if not chunk:
                continue
            try:
                out.append(int(chunk))
            except ValueError:
                continue
        return out

    @property
    def effective_ai_api_key(self) -> str:
        """Prefer AI_API_KEY; fall back to legacy NVIDIA_API_KEY."""
        return self.ai_api_key or self.nvidia_api_key

    @property
    def effective_ai_base_url(self) -> str:
        return self.ai_base_url or self.nvidia_base_url or "https://openrouter.ai/api/v1"

    @property
    def effective_ai_model(self) -> str:
        return self.ai_model or self.nvidia_model or "deepseek/deepseek-v4-flash:free"

    @property
    def db_path(self) -> Path:
        p = Path(self.database_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def log_path(self) -> Path:
        p = Path(self.log_dir)
        p.mkdir(parents=True, exist_ok=True)
        return p


settings = Settings()
