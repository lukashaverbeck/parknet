import sys
from pathlib import Path
sys.path.append(str(Path(sys.path[0]).parent))

import unittest
from vehicle import Agent, Driver


class TestVehicle(unittest.TestCase):
    def setUp(self):
        self.driver_1 = Driver.instance()
        self.driver_2 = Driver.instance()
        
        self.agent_1 = Agent.instance()
        self.agent_2 = Agent.instance()

        return super().setUp()

    def test_driver(self):
        self.assertIs(self.driver_1, self.driver_2)
        self.assertEqual(self.driver_1, self.driver_2)
        
        self.assertEqual(self.driver_1.velocity, 0)
        self.driver_1.accelerate(5)
        self.assertEqual(self.driver_1.velocity, 5)
        self.driver_1.accelerate(-10)
        self.assertEqual(self.driver_1.velocity, -5)
        self.driver_1.accelerate(100)
        self.assertEqual(self.driver_1.velocity, 5)

        self.assertEqual(self.driver_1.angle, 0)
        self.driver_1.steer(35)
        self.assertEqual(self.driver_1.angle, 35)
        self.driver_1.steer(-70)
        self.assertEqual(self.driver_1.angle, -35)
        self.driver_1.steer(100)
        self.assertEqual(self.driver_1.angle, 35)

        self.driver_1.start_recording()
        self.assertIsNotNone(self.driver_1.recorder_thread)
        self.driver_1.stop_recording()
        self.assertIsNone(self.driver_1.recorder_thread)

        self.driver_1.start_driving()
        self.assertIsNotNone(self.driver_1.drive_thread)
        self.driver_1.stop_driving()
        self.assertIsNone(self.driver_1.drive_thread)

    def test_agent(self):
        self.assertIs(self.agent_1, self.agent_2)
        self.assertEqual(self.agent_1, self.agent_2)
        
        self.assertIsNotNone(self.agent_1.id)
        self.assertIsNotNone(self.agent_1.length)
        self.assertIsNotNone(self.agent_1.width)

        self.assertGreater(len(self.agent_1.id), 0)
        self.assertGreater(self.agent_1.length, 0)
        self.assertGreater(self.agent_1.width, 0)


if __name__ == "__main__":
    unittest.main()
