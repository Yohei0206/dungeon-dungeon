from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict


class Role(str, Enum):
    """Playable archetypes in the dungeon.

    The string value keeps saved data readable while still allowing the
    convenience of an Enum.
    """

    WARRIOR = "warrior"
    MAGE = "mage"
    HUNTER = "hunter"
    ROGUE = "rogue"
    MERCHANT = "merchant"
    CLERIC = "cleric"


@dataclass
class Character:
    """Lightweight actor representation used by resolvers.

    Attributes:
        name: Display name.
        role: One of the values from :class:`Role`.
        attack: Base physical or magical damage.
        defense: Flat mitigation against physical attacks.
        luck: Generic chance modifier used across systems.
        hp: Current hit points; clamped to 0 when taking damage.
        gold: Currency tracked by the shop.
        vp: Victory points that can be purchased in the shop.
    """

    name: str
    role: Role
    attack: int
    defense: int
    luck: int
    hp: int
    gold: int = 0
    vp: int = 0

    def apply_damage(self, amount: int) -> int:
        """Reduce hit points while preventing negative HP.

        Args:
            amount: Raw damage value to apply.

        Returns:
            The actual damage taken after clamping.
        """

        taken = max(amount, 0)
        self.hp = max(self.hp - taken, 0)
        return taken

    def heal(self, amount: int) -> int:
        """Simple heal helper used by side quests or items."""

        restored = max(amount, 0)
        self.hp += restored
        return restored

    def adjust_gold(self, delta: int) -> int:
        """Add or remove gold, never dropping below zero."""

        if delta < 0:
            spendable = min(self.gold, -delta)
            self.gold -= spendable
            return spendable * -1
        self.gold += delta
        return delta

    def as_dict(self) -> Dict[str, int | str]:
        """Serialize only the core stats for logging or UI."""

        return {
            "name": self.name,
            "role": self.role.value,
            "attack": self.attack,
            "defense": self.defense,
            "luck": self.luck,
            "hp": self.hp,
            "gold": self.gold,
            "vp": self.vp,
        }
