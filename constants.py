# This module is a collection of global constants divided into multiple classes
# that represent a separate concern.
#
# version:  1.0 (28.12.2019)
#
# TODO define default steering mode file


class Connection:
    WLAN_PASSWORD = "Hallo1234"


class Driving:
    CAUTIOUS_VELOCITY = 7       # cm/s
    STOP_VELOCITY = 0           # cm/s
    MAX_VELOCITY = 7            # cm/s
    MIN_VELOCITY = -7           # cm/s

    MIN_STEERING_ANGLE = -35    # °
    MAX_STEERING_ANGLE = 35     # °
    NEUTRAL_STEERING_ANGLE = 0  # °

    SAFETY_DISTANCE = 3         # cm
    LEAVE_PARKING_LOT_PROPORTION = 0.4


class EchoPin:
    FRONT = 4
    RIGHT = 17
    BACK = 22
    BACK_ANGLED = 27


class Mode:
    ENTER = "parking/enter"
    LEAVE = "parking/leave"
    SEARCH = "parking/search"
    STANDBY = "parking/standby"
    AUTONOMOUS = "drive/follow-road"
    MANUAL = "drive/manual"
    MOVE_UP = "react/move-up"
    MOVE_BACK = "react/move-back"

    ALL = [ENTER, LEAVE, SEARCH, STANDBY, AUTONOMOUS, MANUAL, MOVE_UP, MOVE_BACK]
    DEFAULT = MANUAL


class Stepper:
    DIRECTION_PIN = 20
    STEP_PIN = 21
    SLEEP_PIN = 26


class Storage:
    ATTRIBUTES = "./attributes.json"
    DATA = "./data/"
    CHECKPOINTS = "./checkpoints/"
    DEFAULT_STEERING_MODEL = None  # TODO


class Topic:
    GLOBAL_ACTION_ACTIVE = "action/active-global"
    GLOBAL_ACTION_COMPLETED = "action/completed-global"
    FORMATION_CONFIRMATION = "formation/confirm-backward-pass"
    FORMATION_FORWARD_PASS = "formation/forward-pass"
    FORMATION_BACKWARD_PASS = "formation/backward-pass"


class TriggerPin:
    FRONT = 18
    RIGHT = 23
    BACK = 25
    BACK_ANGLED = 24
