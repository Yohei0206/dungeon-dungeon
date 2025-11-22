from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable, List, Sequence

from .models import Command


class NetSession:
    """Tracks lockstep command exchange and replay validation."""

    def __init__(self, player_order: Sequence[str]):
        self._player_order = list(player_order)
        self._outgoing: List[Command] = []
        self._incoming: Dict[int, List[Command]] = defaultdict(list)
        self._replay_log: List[List[Command]] = []

    def send_command(self, command: Command) -> None:
        """Stage a command to send to peers."""

        self._outgoing.append(command)

    def receive_command(self, turn_index: int, command: Command) -> None:
        """Record a command received from the network for the specified turn."""

        self._incoming[turn_index].append(command)

    def pop_outgoing(self) -> List[Command]:
        """Return staged outgoing commands and clear the send buffer."""

        commands = list(self._outgoing)
        self._outgoing.clear()
        return commands

    def collect_turn_commands(self, turn_index: int) -> List[Command]:
        """Return canonical player-ordered commands for a turn and log them."""

        priority = {player: index for index, player in enumerate(self._player_order)}
        commands = sorted(
            self._incoming.pop(turn_index, []),
            key=lambda cmd: priority.get(cmd.player_id, len(priority)),
        )
        self._replay_log.append(commands)
        return commands

    def verify_replay(self, replay_log: Iterable[Iterable[Command]]) -> bool:
        """Check recorded turns against a replay feed."""

        recorded = [[cmd.player_id + cmd.action for cmd in turn] for turn in self._replay_log]
        replayed = [[cmd.player_id + cmd.action for cmd in turn] for turn in replay_log]
        return recorded == replayed

    @property
    def replay_log(self) -> List[List[Command]]:
        return list(self._replay_log)
