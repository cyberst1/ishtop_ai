"""
Coin purchase packages.

Manual flow:
  1. User picks a package
  2. Bot creates a `coin_purchases` row (status=pending) and returns request id
  3. User pays card-to-card and contacts @cybst_academy with the request id
  4. Admin confirms via admin panel → coins are credited atomically
     and the user gets a Telegram notification.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest

from app.database.repositories import CoinPurchasesRepo
from app.services.coin_economy import CoinEconomy
from app.utils.logger import logger


# ---------- Package catalog ----------

@dataclass(frozen=True)
class Package:
    coins: int
    price: int   # UZS so'm

    @property
    def slug(self) -> str:
        return f"{self.coins}"

    @property
    def label(self) -> str:
        return f"🪙 {self.coins} coin — {self.price:,} so'm".replace(",", " ")


PACKAGES: list[Package] = [
    Package(coins=10,  price=5_000),
    Package(coins=50,  price=19_000),
    Package(coins=100, price=39_000),
    Package(coins=200, price=59_000),
]

PACKAGES_BY_SLUG: dict[str, Package] = {p.slug: p for p in PACKAGES}


def get_package(slug: str) -> Optional[Package]:
    return PACKAGES_BY_SLUG.get(slug)


# ---------- Service ----------

class PurchaseService:
    @staticmethod
    async def create_request(user_id: int, slug: str) -> Optional[tuple[int, Package]]:
        """
        Create a pending purchase. Returns (purchase_id, package) or None if slug invalid.
        """
        pkg = get_package(slug)
        if pkg is None:
            return None
        pid = await CoinPurchasesRepo.create(user_id, pkg.coins, pkg.price)
        logger.info(
            "purchase.created",
            extra={"user_id": user_id, "purchase_id": pid,
                   "coins": pkg.coins, "price": pkg.price},
        )
        return pid, pkg

    @staticmethod
    async def confirm(purchase_id: int, admin_id: int, bot: Bot) -> Optional[dict]:
        """
        Confirm a pending purchase: credit coins + notify user.
        Returns the purchase row (as dict) on success, None if already processed
        or not found.
        """
        purchase = await CoinPurchasesRepo.get(purchase_id)
        if purchase is None or purchase["status"] != "pending":
            return None

        await CoinPurchasesRepo.mark_confirmed(purchase_id, admin_id)
        new_balance = await CoinEconomy.credit(
            purchase["user_id"],
            float(purchase["coins"]),
            reason="purchase",
            related_id=str(purchase_id),
        )

        # Notify the user (best effort)
        try:
            await bot.send_message(
                purchase["user_id"],
                (
                    "✅ *To'lovingiz tasdiqlandi!*\n\n"
                    f"🪙 Hisobingizga: *+{purchase['coins']} coin*\n"
                    f"💳 Yangi balans: *{round(new_balance, 2)} coin*\n\n"
                    f"📌 So'rov ID: `#{purchase_id}`\n\n"
                    "Muvaffaqiyatli ish topishingizni tilaymiz! 🎯"
                ),
            )
        except TelegramBadRequest as e:
            logger.warning("purchase.notify_failed",
                           extra={"user_id": purchase["user_id"],
                                  "purchase_id": purchase_id, "err": str(e)[:200]})
        except Exception:
            logger.exception("purchase.notify_error",
                             extra={"purchase_id": purchase_id})

        logger.info(
            "purchase.confirmed",
            extra={"purchase_id": purchase_id, "admin_id": admin_id,
                   "user_id": purchase["user_id"], "coins": purchase["coins"]},
        )
        return dict(purchase) | {"new_balance": new_balance}

    @staticmethod
    async def reject(purchase_id: int, admin_id: int, bot: Bot,
                     reason: str = "") -> Optional[dict]:
        """Reject a pending purchase + notify user."""
        purchase = await CoinPurchasesRepo.get(purchase_id)
        if purchase is None or purchase["status"] != "pending":
            return None

        await CoinPurchasesRepo.mark_rejected(purchase_id, admin_id, reason)
        try:
            reason_line = f"\n\nSabab: {reason}" if reason else ""
            await bot.send_message(
                purchase["user_id"],
                (
                    f"❌ *To'lov so'rovingiz rad etildi.*\n\n"
                    f"📌 So'rov ID: `#{purchase_id}`\n"
                    f"🪙 So'ralgan: {purchase['coins']} coin\n"
                    f"💵 Narx: {purchase['price']:,} so'm".replace(",", " ")
                    + reason_line +
                    "\n\nQo'shimcha savol bo'lsa: @cybst\\_academy"
                ),
            )
        except Exception:
            logger.exception("purchase.reject_notify_error",
                             extra={"purchase_id": purchase_id})

        logger.info(
            "purchase.rejected",
            extra={"purchase_id": purchase_id, "admin_id": admin_id,
                   "user_id": purchase["user_id"]},
        )
        return dict(purchase)
