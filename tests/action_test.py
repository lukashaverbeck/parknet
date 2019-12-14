import sys
import time
sys.path.append(sys.path[0][:-5])

from vehicle.ActionManager import ActionManager


class TestAgent:
    def __init__(self, agent_id):
        self.__id = agent_id
        self.__action_manager = ActionManager(self)

    def get_id(self):
        return self.__id

    def start_action(self, name):
        self.__action_manager.add_local_action(name)

    def stop_action(self, name):
        self.__action_manager.remove_local_action(name)

    def driver(self):
        return None


agent1 = TestAgent("Agent-1")
agent2 = TestAgent("Agent-2")
agent3 = TestAgent("Agent-3")

time.sleep(2)

agent2.start_action("TEST 1")
agent2.start_action("TEST 1.1")
agent2.stop_action("TEST 1.1")
agent3.start_action("TEST 2")

time.sleep(16)

agent1.start_action("TEST 3")
time.sleep(0.0000001)
agent2.start_action("TEST 4")
time.sleep(0.0000001)
agent3.start_action("TEST 5")