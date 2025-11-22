from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .entities import Character, Role


@dataclass
class TransactionResult:
    success: bool
    gold_spent: int
    gold_gained: int
    vp_gained: int
    message: str


class ShopManager:
    """Handles prices, gold flow, and VP exchanges with class perks."""

    BASE_EXCHANGE_RATE = 10  # gold -> 1 VP

    def __init__(self) -> None:
        self.price_modifiers = {
            Role.MERCHANT: 0.8,  # strong bargaining
            Role.CLERIC: 0.9,  # donations & goodwill
        }
        self.sell_bonus = {
            Role.MERCHANT: 1.25,  # better resale value
            Role.CLERIC: 1.1,  # community support
        }

    def _price_multiplier(self, buyer: Character) -> float:
        return self.price_modifiers.get(buyer.role, 1.0)

    def _sell_multiplier(self, seller: Character) -> float:
        return self.sell_bonus.get(seller.role, 1.0)

    def adjusted_price(self, base_price: int, buyer: Character) -> int:
        multiplier = self._price_multiplier(buyer)
        return max(int(base_price * multiplier), 1)

    def adjusted_sell_price(self, base_price: int, seller: Character) -> int:
        multiplier = self._sell_multiplier(seller)
        return max(int(base_price * 0.5 * multiplier), 1)

    def buy(self, buyer: Character, base_price: int) -> TransactionResult:
        price = self.adjusted_price(base_price, buyer)
        if buyer.gold < price:
            return TransactionResult(False, 0, 0, 0, "Not enough gold")

        buyer.adjust_gold(-price)
        return TransactionResult(True, gold_spent=price, gold_gained=0, vp_gained=0, message="Purchased")

    def sell(self, seller: Character, base_price: int) -> TransactionResult:
        gain = self.adjusted_sell_price(base_price, seller)
        seller.adjust_gold(gain)
        return TransactionResult(True, gold_spent=0, gold_gained=gain, vp_gained=0, message="Sold")

    def exchange_gold_for_vp(self, character: Character, gold_offered: Optional[int] = None) -> TransactionResult:
        """Convert gold into VP, with Merchants receiving the best rate."""

        rate = self.BASE_EXCHANGE_RATE
        if character.role is Role.MERCHANT:
            rate = max(5, int(self.BASE_EXCHANGE_RATE * 0.8))
        elif character.role is Role.CLERIC:
            rate = max(6, int(self.BASE_EXCHANGE_RATE * 0.9))

        available_gold = character.gold if gold_offered is None else min(character.gold, gold_offered)
        vp_to_grant = available_gold // rate
        if vp_to_grant <= 0:
            return TransactionResult(False, 0, 0, 0, "Insufficient gold for VP exchange")

        gold_spent = vp_to_grant * rate
        character.adjust_gold(-gold_spent)
        character.vp += vp_to_grant

        return TransactionResult(
            True,
            gold_spent=gold_spent,
            gold_gained=0,
            vp_gained=vp_to_grant,
            message=f"Exchanged {gold_spent} gold for {vp_to_grant} VP",
        )
