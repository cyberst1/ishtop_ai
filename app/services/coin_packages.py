"""
Coin packages — DISPLAY ONLY.

Users do NOT create purchase requests anymore. They simply see the packages,
pay the admin card-to-card, then message the admin. The admin credits the
coins manually via the user card ("🪙 Coin qo'shish") or the /coin command.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Package:
    coins: int
    price: int        # UZS so'm
    bonus: int = 0    # extra bonus coins

    @property
    def slug(self) -> str:
        return f"{self.coins}"

    @property
    def total_coins(self) -> int:
        return self.coins + self.bonus

    @property
    def label(self) -> str:
        price = f"{self.price:,}".replace(",", " ")
        if self.bonus:
            return f"🪙 {self.coins} (+{self.bonus} bonus) — {price} so'm"
        return f"🪙 {self.coins} coin — {price} so'm"


PACKAGES: list[Package] = [
    Package(coins=10,  price=5_000),
    Package(coins=50,  price=14_000),
    Package(coins=100, price=29_000, bonus=20),
    Package(coins=200, price=49_000, bonus=25),
]

PACKAGES_BY_SLUG: dict[str, Package] = {p.slug: p for p in PACKAGES}


def get_package(slug: str) -> Optional[Package]:
    return PACKAGES_BY_SLUG.get(slug)
