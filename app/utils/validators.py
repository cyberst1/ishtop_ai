"""Common input validators."""
from __future__ import annotations

import re

USERNAME_RE = re.compile(r"^@?[A-Za-z][A-Za-z0-9_]{4,31}$")
TG_USER_ID_RE = re.compile(r"^\d{5,12}$")


def is_valid_username(s: str) -> bool:
    return bool(USERNAME_RE.match(s or ""))


def is_valid_user_id(s: str) -> bool:
    return bool(TG_USER_ID_RE.match(s or ""))


def is_https_url(s: str) -> bool:
    return (s or "").startswith(("https://", "http://"))
