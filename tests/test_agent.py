import unittest

from dungeon_ai.agent import AgentDecisionMaker, AgentState, TileInfo
from dungeon_ai.roles import ROLE_PRIORITIES, Role


class AgentDecisionTests(unittest.TestCase):
    def test_role_priorities_configured(self):
        self.assertGreater(len(ROLE_PRIORITIES), 0)
        hunter_priorities = ROLE_PRIORITIES[Role.HUNTER]
        self.assertGreater(hunter_priorities.exploration, hunter_priorities.combat)

    def test_movement_prefers_visible_and_nearby_tiles(self):
        maker = AgentDecisionMaker(Role.ROGUE)
        current = (0, 0)
        tiles = [
            TileInfo(position=(5, 5), value=9, danger=0.2, is_visible=True),
            TileInfo(position=(1, 0), value=6, danger=0.1, is_visible=True),
            TileInfo(position=(2, 2), value=7, danger=0.8, is_visible=False),
        ]

        choice = maker.select_movement_target(current, tiles)
        self.assertEqual(choice.position, (1, 0))

    def test_hunter_chooses_fallback_under_risk(self):
        maker = AgentDecisionMaker(Role.HUNTER)
        state = AgentState(hp=10, max_hp=100, trap_probability=0.3, escape_success_probability=0.5)
        tiles = [
            TileInfo(position=(0, 1), value=1, danger=0.2),
            TileInfo(position=(1, 1), value=3, danger=0.4),
        ]

        action = maker.choose_safety_action(state, current=(0, 0), visible_tiles=tiles)
        self.assertEqual(action["action"], "fallback")
        self.assertEqual(action["target"].position, (0, 1))

    def test_cleric_prefers_heal_when_weakened(self):
        maker = AgentDecisionMaker(Role.CLERIC)
        state = AgentState(hp=15, max_hp=100, trap_probability=0.0, escape_success_probability=1.0)
        tiles = [
            TileInfo(position=(0, 1), value=5, danger=0.1),
        ]

        action = maker.choose_safety_action(state, current=(0, 0), visible_tiles=tiles)
        self.assertEqual(action["action"], "heal")
        self.assertEqual(action["target"].position, (0, 1))

    def test_low_risk_roles_advance(self):
        maker = AgentDecisionMaker(Role.WARRIOR)
        state = AgentState(hp=90, max_hp=100, trap_probability=0.0, escape_success_probability=0.9)
        tiles = [
            TileInfo(position=(0, 1), value=5, danger=0.1),
            TileInfo(position=(0, 2), value=7, danger=0.4),
        ]

        action = maker.choose_safety_action(state, current=(0, 0), visible_tiles=tiles)
        self.assertEqual(action["action"], "advance")
        self.assertEqual(action["target"].position, (0, 1))


if __name__ == "__main__":
    unittest.main()
