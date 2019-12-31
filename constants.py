# This module is a collection of global constants divided into multiple classes
# that represent a separate concern.
#
# author:   @lukashaverbeck
# author:   @LunaNordin
# version:  2.0 (28.12.2019)


class Connection:
    WLAN_PASSWORD = "42Rkc#oR"


class Driving:
    CAUTIOUS_VELOCITY = 5       # cm/s
    STOP_VELOCITY = 0           # cm/s
    MAX_VELOCITY = 5            # cm/s
    MIN_VELOCITY = -5           # cm/s

    MIN_STEERING_ANGLE = -35    # °
    MAX_STEERING_ANGLE = 35     # °
    NEUTRAL_STEERING_ANGLE = 0  # °

    SAFETY_DISTANCE = 3         # cm
    LEAVE_PARKING_LOT_PROPORTION = 0.4


class EchoPin:
    FRONT = 24
    RIGHT = 27
    BACK = 17
    BACK_ANGLED = 10


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


class Topic:
    GLOBAL_ACTION_ACTIVE = "action/active-global"
    GLOBAL_ACTION_COMPLETED = "action/completed-global"
    FORMATION_CONFIRMATION = "formation/confirm-backward-pass"
    FORMATION_FORWARD_PASS = "formation/forward-pass"
    FORMATION_BACKWARD_PASS = "formation/backward-pass"


class TriggerPin:
    FRONT = 23
    RIGHT = 22
    BACK = 4
    BACK_ANGLED = 18
