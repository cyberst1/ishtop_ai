"""bcrypt password hashing (cost 12)."""
from __future__ import annotations

import bcrypt


def hash_password(plain: str, *, cost: int = 12) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt(cost)).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    if not plain or not hashed:
        return False
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False
