from __future__ import annotations

import random
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional

from .entities import Character, Role


class EventType(str, Enum):
    TRAP = "trap"
    CHEST = "chest"
    SIDE_QUEST = "side_quest"


@dataclass
class DamageResult:
    damage: int
    defender_hp: int
    escaped: bool = False


@dataclass
class EventResult:
    event: EventType
    outcome: str
    details: Dict[str, int | str]


class CombatResolver:
    """Resolves combat outcomes including class perks and escape checks."""

    HUNTER_BONUS_RATIO = 0.25

    def __init__(self, rng: Optional[random.Random] = None) -> None:
        self.rng = rng or random.Random()

    def calculate_damage(self, attacker: Character, defender: Character) -> int:
        """Compute damage with Mage defense ignore and Hunter bonus damage."""

        effective_defense = 0 if attacker.role is Role.MAGE else defender.defense
        base_damage = max(attacker.attack - effective_defense, 1)

        if attacker.role is Role.HUNTER:
            bonus = max(int(base_damage * self.HUNTER_BONUS_RATIO), 1)
            base_damage += bonus

        return base_damage

    def attempt_escape(self, actor: Character, threat_level: int = 1) -> bool:
        """Luck-driven flee chance that scales with perceived danger."""

        difficulty = max(threat_level, 1)
        escape_chance = min(0.9, 0.3 + actor.luck / 150) / difficulty
        return self.rng.random() < escape_chance

    def resolve_attack(self, attacker: Character, defender: Character) -> DamageResult:
        """Apply damage and report the defender's resulting HP."""

        damage = self.calculate_damage(attacker, defender)
        remaining_hp = defender.hp - damage
        defender.apply_damage(damage)
        return DamageResult(damage=damage, defender_hp=max(remaining_hp, 0))

    def resolve_turn(
        self, attacker: Character, defender: Character, can_escape: bool = False, threat_level: int = 1
    ) -> DamageResult:
        """Run a single combat turn with optional escape resolution."""

        if can_escape and self.attempt_escape(attacker, threat_level):
            return DamageResult(damage=0, defender_hp=defender.hp, escaped=True)

        return self.resolve_attack(attacker, defender)


class EventResolver:
    """Handles non-combat events influenced by the adventurer's luck."""

    def __init__(self, rng: Optional[random.Random] = None) -> None:
        self.rng = rng or random.Random()

    def _luck_roll(self, luck: int) -> float:
        return min(0.95, 0.25 + luck / 120)

    def resolve_trap(self, character: Character) -> EventResult:
        avoid_chance = self._luck_roll(character.luck)
        if character.role is Role.ROGUE:
            avoid_chance += 0.2

        avoided = self.rng.random() < avoid_chance
        if avoided:
            return EventResult(event=EventType.TRAP, outcome="avoided", details={"hp": character.hp})

        base_damage = 12
        mitigation = int(character.defense * 0.5)
        damage = max(base_damage - mitigation, 3)
        character.apply_damage(damage)
        return EventResult(event=EventType.TRAP, outcome="hit", details={"damage": damage, "hp": character.hp})

    def resolve_chest(self, character: Character) -> EventResult:
        rare_threshold = self._luck_roll(character.luck)
        if character.role is Role.ROGUE:
            rare_threshold += 0.15

        roll = self.rng.random()
        if roll < rare_threshold:
            reward = "rare"
            gold = 50
        else:
            reward = "common"
            gold = 20

        character.adjust_gold(gold)
        return EventResult(
            event=EventType.CHEST,
            outcome=reward,
            details={"gold": gold, "total_gold": character.gold},
        )

    def resolve_side_quest(self, character: Character) -> EventResult:
        success_chance = self._luck_roll(character.luck)
        roll = self.rng.random()
        if roll < success_chance:
            heal_amount = 8
            reward_gold = 15
            character.heal(heal_amount)
            character.adjust_gold(reward_gold)
            outcome = "success"
            details = {"heal": heal_amount, "gold": reward_gold, "hp": character.hp, "total_gold": character.gold}
        else:
            fatigue = 4
            character.apply_damage(fatigue)
            outcome = "failed"
            details = {"fatigue": fatigue, "hp": character.hp}

        return EventResult(event=EventType.SIDE_QUEST, outcome=outcome, details=details)

    def resolve(self, event: EventType, character: Character) -> EventResult:
        if event is EventType.TRAP:
            return self.resolve_trap(character)
        if event is EventType.CHEST:
            return self.resolve_chest(character)
        if event is EventType.SIDE_QUEST:
            return self.resolve_side_quest(character)
        raise ValueError(f"Unsupported event type: {event}")
