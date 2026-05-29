"""Structured JSON logger. Never logs the bot token."""
from __future__ import annotations

import json
import logging
import sys
from datetime import datetime
from pathlib import Path

_SENSITIVE_KEYS = {"bot_token", "password", "admin_password_hash", "hmac_secret",
                   "nvidia_api_key", "linkedin_cookie", "tg_api_hash"}


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        for k, v in record.__dict__.items():
            if k in ("args", "msg", "levelname", "levelno", "pathname", "filename",
                     "module", "exc_info", "exc_text", "stack_info", "lineno",
                     "funcName", "created", "msecs", "relativeCreated", "thread",
                     "threadName", "processName", "process", "name", "taskName"):
                continue
            if k.lower() in _SENSITIVE_KEYS:
                v = "***"
            try:
                json.dumps(v)
                payload[k] = v
            except Exception:
                payload[k] = str(v)
        return json.dumps(payload, ensure_ascii=False)


def _build_logger() -> logging.Logger:
    log = logging.getLogger("ish_top_ai")
    if log.handlers:
        return log

    # avoid importing settings at module top to prevent circular import
    try:
        from app.config import settings
        level = settings.log_level
        log_dir = Path(settings.log_dir)
    except Exception:
        level = "INFO"
        log_dir = Path("data/logs")

    log.setLevel(getattr(logging, level, logging.INFO))
    log_dir.mkdir(parents=True, exist_ok=True)

    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(JsonFormatter())
    log.addHandler(sh)

    fh = logging.FileHandler(log_dir / "bot.log", encoding="utf-8")
    fh.setFormatter(JsonFormatter())
    log.addHandler(fh)

    log.propagate = False
    return log


logger = _build_logger()
