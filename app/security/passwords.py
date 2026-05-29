"""bcrypt password hashing (cost 12) + flexible verification."""
from __future__ import annotations

import bcrypt


def hash_password(plain: str, *, cost: int = 12) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt(cost)).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """
    Accepts either a real bcrypt hash or a corrupted hash (e.g. with $ signs
    eaten by .env interpolation).  Returns True only on a clean bcrypt match.
    """
    if not plain or not hashed:
        return False
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def verify_admin(plain: str, *, hashed: str = "", plaintext: str = "") -> bool:
    """
    Verify admin password against either:
      - bcrypt hash (preferred, set ADMIN_PASSWORD_HASH in .env), OR
      - plain text password (set ADMIN_PASSWORD in .env, easier for non-techies)

    Returns True if EITHER matches.  Plain comparison is constant-time.
    """
    if not plain:
        return False
    plain = plain.strip()

    # 1) Bcrypt path
    if hashed and hashed.startswith("$2"):
        if verify_password(plain, hashed):
            return True

    # 2) Plain text fallback (constant-time)
    if plaintext:
        if _consteq(plain, plaintext.strip()):
            return True

    return False


def _consteq(a: str, b: str) -> bool:
    if len(a) != len(b):
        return False
    res = 0
    for x, y in zip(a.encode(), b.encode()):
        res |= x ^ y
    return res == 0
