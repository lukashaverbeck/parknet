import random
import time

import control

_driver = control.Driver()


def test_drive_for() -> None:
    """ Tests whether driving for a specific amount of time works properly.

    Setup:
        One agent on clear track. Activate the agent's driving hardware. Run the test.

    Expected Results:
        The agent drives forward for about five seconds with a slow and steady velocity.
        The agent stops.
        The agent drives backward for about five seconds with a slow and steady velocity.
    """

    _driver.forward.do_for(5)
    _driver.backward.do_for(5)


def test_drive_while() -> None:
    """ Tests whether driving as long as a specific condition is met works properly.

    Setup:
        One agent on clear track. Activate the agent's driving hardware. Run the test.

    Expected Results:
        The agent drives forward forward.
        The agent stops driving forward as soon as ``Stop!`` is printed in the terminal.
        The agent drives forward forward.
        The agent stops driving backward as soon as ``Stop!`` is printed in the terminal.
    """

    def condition() -> bool:
        if random.randint(0, 100) >= 95:
            print("Stop!")
            return False

        return True

    _driver.forward.do_while(condition)
    _driver.backward.do_while(condition)


def test_steering() -> None:
    """ Tests whether adjusting the steering angle works properly.

    Setup:
        One agent. Activate the agent's driving hardware. Run the test.

    Expected Results:
        The agent adjusts the steering angle to about 10°.
        After five seconds, the agent adjusts the steering angle to about -10°.
        After five seconds, the agent adjusts the steering angle to maximum right steering angle.
        After five seconds, the agent adjusts the steering angle to maximum left steering angle.
    """

    angles = [0, 10, -10, 9999, -9999]
    for angle in angles:
        _driver.steer(angle)
        time.sleep(5)


def test_safety_distance_keeping() -> None:
    """ Tests whether the agent always maintains safety distances.

    Setup:
        One agent. Obstacle close in front and behind the agent. Activate the agent's driving hardware. Run the test.

    Expected Results:
        The agent does nothing.
    """

    _driver.forward.do_for(2)
    _driver.backward.do_for(2)


def test_stop() -> None:
    """ Tests whether stopping a driving mode works properly.

    Setup:
        One agent on clear track. Activate the agent's driving hardware. Run the test.

    Expected Results:
        The agent does nothing.
    """

    mode = _driver.forward
    mode.stop()
    mode.do_for(9999)
