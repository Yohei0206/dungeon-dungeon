from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Role(str, Enum):
    WARRIOR = "Warrior"
    HUNTER = "Hunter"
    CLERIC = "Cleric"
    ROGUE = "Rogue"
    MAGE = "Mage"


@dataclass(frozen=True)
class RolePriorities:
    exploration: float
    combat: float
    economy: float


ROLE_PRIORITIES: dict[Role, RolePriorities] = {
    Role.WARRIOR: RolePriorities(exploration=0.6, combat=0.9, economy=0.5),
    Role.HUNTER: RolePriorities(exploration=0.8, combat=0.6, economy=0.5),
    Role.CLERIC: RolePriorities(exploration=0.55, combat=0.55, economy=0.7),
    Role.ROGUE: RolePriorities(exploration=0.9, combat=0.45, economy=0.85),
    Role.MAGE: RolePriorities(exploration=0.7, combat=0.65, economy=0.6),
}


def get_role_priorities(role: Role) -> RolePriorities:
    """Return tuned priorities for the requested role.

    Priorities stay normalized around 0-1 and can be combined with other
    heuristics to favor actions that align with the profession fantasy.
    """

    try:
        return ROLE_PRIORITIES[role]
    except KeyError as exc:  # pragma: no cover - defensive guard
        raise ValueError(f"Unknown role: {role}") from exc
