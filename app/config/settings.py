"""
Centralized configuration via pydantic-settings.
Loads from environment / .env. NEVER log the bot token.
"""
from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ---- Telegram ----
    bot_token: str = Field(..., min_length=20)
    bot_username: str = "ish_top_ai_bot"

    # ---- Admin ----
    # Stored as a raw string ("123" or "123,456") and exposed as a list
    # via the `admin_ids` property below.  This sidesteps pydantic-settings'
    # JSON parsing for List[int] env values.
    admin_ids_raw: str = Field(default="", alias="ADMIN_IDS")
    admin_password_hash: str = ""
    admin_session_ttl_minutes: int = 30

    # ---- AI ----
    nvidia_api_key: str = ""
    nvidia_base_url: str = "https://integrate.api.nvidia.com/v1"
    nvidia_model: str = "meta/llama-3.1-70b-instruct"

    # ---- Database ----
    database_path: str = "data/ish_top_ai.db"

    # ---- Mode ----
    mode: str = "polling"  # polling | webhook
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
    # Optional[int] so an empty .env value (TG_API_ID=) maps cleanly to None.
    tg_api_id: Optional[int] = None
    tg_api_hash: str = ""

    # ---- Economy constants ----
    signup_gift_coins: float = 4.0
    job_unlock_cost: float = 2.0
    referral_first_bonus: float = 2.0
    referral_next_bonus: float = 1.0
    bonus_channel_reward: float = 0.5
    free_daily_searches: int = 3

    # ---- Pricing (so'm) ----
    premium_price: int = 9_000
    premium_plus_price: int = 19_990

    # -------------------- validators --------------------

    @field_validator("tg_api_id", mode="before")
    @classmethod
    def _parse_tg_api_id(cls, v):
        if v is None or v == "":
            return None
        return v

    # Generic: any int field that receives an empty string from .env
    # should fall back to the field's default value.
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
    def db_path(self) -> Path:
        p = Path(self.database_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def log_path(self) -> Path:
        p = Path(self.log_dir)
        p.mkdir(parents=True, exist_ok=True)
        return p


settings = Settings()  # raises if BOT_TOKEN is missing
