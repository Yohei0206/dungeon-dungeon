from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Callable, Dict, Iterable, List, Sequence

from .models import ActionResult, Command


@dataclass(slots=True)
class QueuedCommand:
    turn_index: int
    command: Command


class TurnController:
    """Coordinates player order, input queues, and action resolution for a turn.

    The controller is agnostic to the concrete game rules. It delegates per-action
    resolution to ``action_resolver`` and only guarantees ordering and queue
    integrity.
    """

    def __init__(
        self,
        player_order: Sequence[str],
        action_resolver: Callable[[Command, int], ActionResult],
    ) -> None:
        self._player_order: List[str] = list(player_order)
        self._action_resolver = action_resolver
        self._input_queues: Dict[int, List[QueuedCommand]] = defaultdict(list)

    @property
    def player_order(self) -> List[str]:
        return list(self._player_order)

    def queue_input(self, turn_index: int, command: Command) -> None:
        """Add a player command to the queue for a given turn."""

        self._input_queues[turn_index].append(QueuedCommand(turn_index, command))

    def resolve_turn(self, turn_index: int) -> List[ActionResult]:
        """Resolve queued commands for the target turn in player order."""

        queued = self._input_queues.pop(turn_index, [])
        sorted_commands = self._sort_by_player_order(queued)

        return [self._action_resolver(entry.command, turn_index) for entry in sorted_commands]

    def _sort_by_player_order(self, commands: Iterable[QueuedCommand]) -> List[QueuedCommand]:
        priority = {player: index for index, player in enumerate(self._player_order)}
        return sorted(commands, key=lambda entry: priority.get(entry.command.player_id, len(priority)))
