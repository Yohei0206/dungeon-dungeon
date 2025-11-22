from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


@dataclass(slots=True)
class PlayerState:
    """Represents the current score for a participant.

    The manager tracks victory points (VP) centrally, so this object only stores
    the player's identifier and running VP total.
    """

    player_id: str
    victory_points: int = 0

    def apply_vp(self, delta: int) -> None:
        """Apply a VP delta to the player.

        Args:
            delta: Positive or negative VP gained this turn.
        """

        self.victory_points += delta


@dataclass(slots=True)
class Command:
    """An action request issued by a player.

    Attributes:
        player_id: Owner of the command.
        action: The action identifier the game will resolve.
        payload: Optional structured data sent alongside the action.
    """

    player_id: str
    action: str
    payload: Dict[str, object] = field(default_factory=dict)


@dataclass(slots=True)
class ActionResult:
    """Outcome of resolving a single command for a turn."""

    player_id: str
    turn_index: int
    vp_delta: int = 0
    events: Dict[str, object] = field(default_factory=dict)
