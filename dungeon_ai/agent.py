from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

from .roles import Role, RolePriorities, get_role_priorities


@dataclass(frozen=True)
class TileInfo:
    """Information about a tile the agent can consider stepping on."""

    position: tuple[int, int]
    value: float
    danger: float
    is_visible: bool = True


@dataclass
class AgentState:
    hp: int
    max_hp: int
    trap_probability: float
    escape_success_probability: float

    @property
    def hp_ratio(self) -> float:
        return 0 if self.max_hp <= 0 else max(0.0, min(1.0, self.hp / self.max_hp))


class AgentDecisionMaker:
    """Combine priorities, visibility, and risk to decide movement and safety."""

    distance_weight: float = 0.8
    danger_weight: float = 1.2

    def __init__(self, role: Role):
        self.role = role
        self.priorities: RolePriorities = get_role_priorities(role)

    @staticmethod
    def _manhattan(a: tuple[int, int], b: tuple[int, int]) -> int:
        ax, ay = a
        bx, by = b
        return abs(ax - bx) + abs(ay - by)

    def _distance_penalty(self, current: tuple[int, int], tile: TileInfo) -> float:
        distance = self._manhattan(current, tile.position)
        return distance * self.distance_weight

    def select_movement_target(
        self, current: tuple[int, int], visible_tiles: Iterable[TileInfo]
    ) -> Optional[TileInfo]:
        """Pick the next tile using visibility and distance heuristics.

        * Only visible tiles participate.
        * High-value tiles are weighted with exploration/economy priorities.
        * Dangerous or distant tiles are penalized, especially for cautious roles.
        """

        best_tile: Optional[TileInfo] = None
        best_score = float("-inf")

        for tile in visible_tiles:
            if not tile.is_visible:
                continue

            value_weight = (self.priorities.exploration + self.priorities.economy) / 2
            combat_bias = (1 - self.priorities.combat) * 0.5
            score = (tile.value * value_weight) - (
                tile.danger * self.danger_weight * (1 + combat_bias)
            )
            score -= self._distance_penalty(current, tile)

            if self.role in {Role.HUNTER, Role.CLERIC}:
                score -= tile.danger * 0.2  # extra caution on dangerous tiles

            if score > best_score:
                best_score = score
                best_tile = tile

        return best_tile

    def assess_risk(self, state: AgentState) -> float:
        """Evaluate overall risk using HP, traps, and escape odds."""

        hp_pressure = (1 - state.hp_ratio) * 0.6
        trap_pressure = state.trap_probability * 0.25
        escape_pressure = (1 - state.escape_success_probability) * 0.15

        risk = hp_pressure + trap_pressure + escape_pressure

        if self.role in {Role.HUNTER, Role.CLERIC}:
            risk *= 1.15  # more conservative safety margin

        return max(0.0, min(1.0, risk))

    def choose_safety_action(
        self, state: AgentState, current: tuple[int, int], visible_tiles: Iterable[TileInfo]
    ) -> dict[str, Optional[object]]:
        """Select a safety-conscious action considering the risk assessment.

        Returns a dict containing the action name and the selected target tile if any.
        """

        risk = self.assess_risk(state)
        caution_threshold = 0.35 if self.role in {Role.HUNTER, Role.CLERIC} else 0.5

        if self.role == Role.CLERIC and state.hp_ratio < 0.4:
            target = self._select_low_danger_tile(current, visible_tiles)
            return {"action": "heal", "target": target, "risk": risk}

        if risk >= caution_threshold:
            target = self._select_low_danger_tile(current, visible_tiles)
            return {"action": "fallback", "target": target, "risk": risk}

        target = self.select_movement_target(current, visible_tiles)
        return {"action": "advance", "target": target, "risk": risk}

    def _select_low_danger_tile(
        self, current: tuple[int, int], visible_tiles: Iterable[TileInfo]
    ) -> Optional[TileInfo]:
        """Find the closest tile that minimizes danger for safe retreat."""

        candidate: Optional[TileInfo] = None
        best_tuple: Optional[tuple[float, float]] = None

        for tile in visible_tiles:
            if not tile.is_visible:
                continue

            distance = self._manhattan(current, tile.position)
            ranking = (tile.danger, distance)

            if best_tuple is None or ranking < best_tuple:
                best_tuple = ranking
                candidate = tile

        return candidate
