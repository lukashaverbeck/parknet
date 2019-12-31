import sys
from pathlib import Path
sys.path.append(str(Path(sys.path[0]).parent))

import unittest
from vehicle import Agent
from connection import Server
from interaction import Communication, Message, ActionManager, Action


class TestInteraction(unittest.TestCase):
    def setUp(self):
        self.agent = Agent.instance()

        self.communication_1 = Communication.instance()
        self.communication_2 = Communication.instance()

        self.message = Message(self.agent, "topic", None)

        self.action_manager_1 = ActionManager.instance()
        self.action_manager_2 = ActionManager.instance()

        self.action = Action(self.agent, "parking/enter")
        return super().setUp()

    def test_communication(self):
        self.assertEqual(self.communication_1, self.communication_2)
        self.assertIs(self.communication_1, self.communication_2)
        
        self.assertIsNotNone(Server.communication)
        self.assertIsNotNone(self.communication_1.agent)

        self.communication_1.subscribe("topic", None)
        self.assertGreater(len(self.communication_1.subscriptions), 0)

    def test_message(self):
        self.assertEqual(self.agent.id, self.message.sender)

    def test_action_manager(self):
        self.assertEqual(self.action_manager_1, self.action_manager_2)
        self.assertIs(self.action_manager_1, self.action_manager_2)

        self.action_manager_1.append("parking/enter")
        self.action_manager_1.append("parking/enter")
        self.action_manager_1.append("parking/enter")
        self.action_manager_1.append("parking/leave")
        self.action_manager_1.append("parking/enter")
        self.action_manager_1.append("parking/leave")
        self.action_manager_1.remove("parking/enter")
        self.assertEqual(len(self.action_manager_1.local_actions), 2)

    def test_action(self):
        self.assertEqual(self.action.agent, self.agent.id)
        self.assertTrue(self.action.is_owner(self.agent))


if __name__ == "__main__":
    unittest.main()
