"""HMAC-signed callback tokens — prevent forgery and replay."""
from __future__ import annotations

import hmac
import hashlib
import time
from base64 import urlsafe_b64decode, urlsafe_b64encode

from app.config import settings


def _key() -> bytes:
    return settings.hmac_secret.encode("utf-8")


def sign_callback(payload: str, *, ttl: int = 600) -> str:
    """Returns 'payload|ts|sig' (base64-safe). Total length should stay <64 for callback_data."""
    ts = str(int(time.time()))
    raw = f"{payload}|{ts}".encode("utf-8")
    sig = hmac.new(_key(), raw, hashlib.sha256).digest()[:8]  # 8 bytes is enough here
    sig_b64 = urlsafe_b64encode(sig).rstrip(b"=").decode()
    return f"{payload}|{ts}|{sig_b64}"


def verify_callback(token: str, *, ttl: int = 600) -> str | None:
    try:
        payload, ts, sig_b64 = token.rsplit("|", 2)
        if int(time.time()) - int(ts) > ttl:
            return None
        raw = f"{payload}|{ts}".encode("utf-8")
        expected = hmac.new(_key(), raw, hashlib.sha256).digest()[:8]
        pad = "=" * (-len(sig_b64) % 4)
        actual = urlsafe_b64decode(sig_b64 + pad)
        if hmac.compare_digest(expected, actual):
            return payload
    except (ValueError, TypeError):
        return None
    return None
