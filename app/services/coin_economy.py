"""
Coin economy — atomic credit/debit with full audit trail in `balances` ledger.
NEVER mutate users.coin_balance directly: always go through this service.
"""
from __future__ import annotations

from app.database.engine import get_db


class CoinEconomy:
    @staticmethod
    async def balance(user_id: int) -> float:
        row = await get_db().fetchone(
            "SELECT coin_balance FROM users WHERE user_id = ?", (user_id,)
        )
        return float(row["coin_balance"]) if row else 0.0

    @staticmethod
    async def adjust(user_id: int, delta: float, *, reason: str,
                     related_id: str | None = None) -> float:
        """
        Atomic: lock row → update balance → write ledger entry.
        Returns new balance. Raises ValueError if user is missing.
        """
        db = get_db()
        async with db.cursor() as cur:
            await cur.execute(
                "SELECT coin_balance FROM users WHERE user_id = ?", (user_id,)
            )
            row = await cur.fetchone()
            if row is None:
                raise ValueError(f"User {user_id} not found")
            new_bal = round(float(row["coin_balance"]) + float(delta), 4)
            await cur.execute(
                "UPDATE users SET coin_balance = ? WHERE user_id = ?",
                (new_bal, user_id),
            )
            await cur.execute(
                """INSERT INTO balances (user_id, delta, reason, related_id, balance_after)
                   VALUES (?, ?, ?, ?, ?)""",
                (user_id, float(delta), reason, related_id, new_bal),
            )
        return new_bal

    @staticmethod
    async def spend(user_id: int, amount: float, *, reason: str,
                    related_id: str | None = None) -> tuple[bool, float]:
        """
        Try to debit `amount` from user. Returns (success, current_balance).
        If balance is insufficient, returns (False, balance) without changes.
        """
        bal = await CoinEconomy.balance(user_id)
        if bal < amount:
            return False, bal
        new_bal = await CoinEconomy.adjust(user_id, -amount, reason=reason, related_id=related_id)
        return True, new_bal

    @staticmethod
    async def credit(user_id: int, amount: float, *, reason: str,
                     related_id: str | None = None) -> float:
        return await CoinEconomy.adjust(user_id, amount, reason=reason, related_id=related_id)
