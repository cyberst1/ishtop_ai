"""
Centralized configuration via pydantic-settings.
Loads from environment / .env. NEVER log the bot token.
"""
from __future__ import annotations

from pathlib import Path
from typing import List

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
    admin_ids: List[int] = Field(default_factory=list)
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
    tg_api_id: int = 0
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

    @field_validator("admin_ids", mode="before")
    @classmethod
    def parse_admin_ids(cls, v):
        if isinstance(v, str):
            return [int(x.strip()) for x in v.split(",") if x.strip()]
        return v or []

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
