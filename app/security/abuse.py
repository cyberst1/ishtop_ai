"""
Heuristic abuse detection: multi-account / referral abuse.

Real production would also use:
 - device fingerprinting (Telegram WebApp data)
 - IP heuristics (only available with webhook)
 - graph clustering of referral chains
"""
from __future__ import annotations

from datetime import datetime, timedelta

from app.database.engine import get_db


class AbuseDetector:
    @staticmethod
    async def is_suspicious_referral(referrer_id: int, referred_id: int) -> bool:
        if referrer_id == referred_id:
            return True
        db = get_db()
        # Reject if referrer already invited >50 in 24h
        row = await db.fetchone(
            """SELECT COUNT(*) AS c FROM referrals
               WHERE referrer_id = ? AND created_at > datetime('now', '-1 day')""",
            (referrer_id,),
        )
        if row and row["c"] > 50:
            return True
        # Reject if referrer and referred created in same minute (likely same person)
        row = await db.fetchone(
            """SELECT
                   ABS(strftime('%s', a.created_at) - strftime('%s', b.created_at)) AS dt
               FROM users a, users b
               WHERE a.user_id = ? AND b.user_id = ?""",
            (referrer_id, referred_id),
        )
        if row and row["dt"] is not None and row["dt"] < 60:
            return True
        return False
