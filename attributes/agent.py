import json
import os.path
from typing import List

import util

_ATTRIBUTES_DIR: str = os.path.dirname(os.path.abspath(__file__))
_ATTRIBUTES_PATH: str = os.path.join(_ATTRIBUTES_DIR, "agent.json")
_INITIALIZED: bool = False


class _Keys:
    SIGNATURE: str = "signature"
    DELTA: str = "delta"
    STEERING_PARAMETERS: str = "steering"


SIGNATURE: str
DELTA: float
STEERING_PARAMETERS: List[float]

# there must be an attributes file in the root directory of the project
assert os.path.exists(_ATTRIBUTES_PATH), f"Agent attributes ({_ATTRIBUTES_PATH}) is missing."


def initialize() -> None:
    """ Sets the main agent's signature and delta based on the ``agent.json`` file.

    After successful initialization the main initialization flagged with ``INITIALIZED = True``.

    Raises:
        AssertionError: If attributes file does not contain the required agent information.
    """

    global SIGNATURE, DELTA, STEERING_PARAMETERS, _INITIALIZED

    # open attributes file
    with open(_ATTRIBUTES_PATH) as attributes_file:
        # parse json data to dictionary
        attributes = json.load(attributes_file)

        # the attributes must include the agent's signature and delta
        util.assert_keys_exist([_Keys.SIGNATURE, _Keys.DELTA, _Keys.STEERING_PARAMETERS], attributes)

        # set the main agent's signature, delta and steering parameters and the initialization flag
        SIGNATURE = attributes[_Keys.SIGNATURE]
        DELTA = attributes[_Keys.DELTA]
        STEERING_PARAMETERS = attributes[_Keys.STEERING_PARAMETERS]
        _INITIALIZED = True


# always initialize attributes when loaded
if not _INITIALIZED:
    initialize()
