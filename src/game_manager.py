from __future__ import annotations

from typing import Callable, Dict, Iterable, List, Optional

from .models import ActionResult, Command, PlayerState
from .net_session import NetSession
from .turn_controller import TurnController

TurnActionResolver = Callable[[Command, int], ActionResult]


class GameManager:
    """Controls 30-turn progression and victory point (VP) scoring."""

    TURN_LIMIT = 30

    def __init__(
        self,
        player_ids: Iterable[str],
        action_resolver: TurnActionResolver,
        net_session: Optional[NetSession] = None,
    ) -> None:
        self.players: Dict[str, PlayerState] = {pid: PlayerState(pid) for pid in player_ids}
        self.turn_controller = TurnController(player_order=list(player_ids), action_resolver=action_resolver)
        self.net_session = net_session or NetSession(player_order=list(player_ids))
        self.turn_index = 0

    def enqueue_commands(self, commands: Iterable[Command]) -> None:
        """Queue local player commands for the current turn and stage them for sending."""

        for command in commands:
            if command.player_id not in self.players:
                raise ValueError(f"Unknown player: {command.player_id}")
            self.turn_controller.queue_input(self.turn_index, command)
            self.net_session.send_command(command)

    def receive_remote_commands(self, commands: Iterable[Command]) -> None:
        """Inject remote commands received over the network for this turn."""

        for command in commands:
            self.net_session.receive_command(self.turn_index, command)
            self.turn_controller.queue_input(self.turn_index, command)

    def resolve_current_turn(self) -> List[ActionResult]:
        """Resolve the current turn and apply VP updates."""

        if self.turn_index >= self.TURN_LIMIT:
            raise RuntimeError("Turn limit reached")

        ordered_commands = self.net_session.collect_turn_commands(self.turn_index)
        # Ensure the collected commands are queued even if they were already added via receive_remote_commands
        for command in ordered_commands:
            self.turn_controller.queue_input(self.turn_index, command)

        results = self.turn_controller.resolve_turn(self.turn_index)
        for result in results:
            self.players[result.player_id].apply_vp(result.vp_delta)

        self.turn_index += 1
        return results

    def run_full_game(self, per_turn_commands: Dict[int, Iterable[Command]]) -> List[List[ActionResult]]:
        """Convenience helper for running a 30-turn loop in offline tests."""

        history: List[List[ActionResult]] = []
        while self.turn_index < self.TURN_LIMIT:
            commands = per_turn_commands.get(self.turn_index, [])
            self.enqueue_commands(commands)
            turn_results = self.resolve_current_turn()
            history.append(turn_results)
        return history

    def standings(self) -> Dict[str, int]:
        """Return the current VP tally for all players."""

        return {pid: player.victory_points for pid, player in self.players.items()}
