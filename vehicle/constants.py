# collection of global constants
# author:   @lukashaverbeck
# author:   @LunaNordin
# version:  1.1.1(27.12.2019)


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


class Driving:
    CAUTIOUS_VELOCITY = 308  # pwm
    STOP_VELOCITY = 340  # pwm
    MAX_VELOCITY = 360  # pwm
    MIN_VELOCITY = 320  # pwm

    MIN_STEERING_ANGLE = -35
    MAX_STEERING_ANGLE = 35
    NEUTRAL_STEERING_ANGLE = 0


class Stepper:
    DIRECTION_PIN = 20
    STEP_PIN = 21
    SLEEP_PIN = 26


class Direction:
    FRONT = 0
    RIGHT = 1
    BACK = 2
    BACK_ANGLED = 3


class File:
    ATTRIBUTES = "./attributes.json"


class TriggerPin:
    HC_SR04_FRONT = 23
    HC_SR04_RIGHT = 22
    HC_SR04_BACK = 4
    HC_SR04_BACK_ANGLED = 18


class EchoPin:
    HC_SR04_FRONT = 24
    HC_SR04_RIGHT = 27
    HC_SR04_BACK = 17
    HC_SR04_BACK_ANGLED = 10


class Topic:
    GLOBAL_ACTION_ACTIVE = "action/active-global"
    GLOBAL_ACTION_COMPLETED = "action/completed-global"
    FORMATION_CONFIRMATION = "formation/confirm-backward-pass"
    FORMATION_FORWARD_PASS = "formation/forward-pass"
    FORMATION_BACKWARD_PASS = "formation/backward-pass"
