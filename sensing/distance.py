from datetime import datetime

from gpiozero import DistanceSensor

UPDATE_INTERVAL: float = 0.4


class _TriggerPins:
    FRONT: int = 18
    RIGHT: int = 23
    BACK: int = 25
    BACK_ANGLED: int = 24


class _EchoPins:
    FRONT: int = 4
    RIGHT: int = 17
    BACK: int = 22
    BACK_ANGLED: int = 27


class _UltrasonicSensor:
    @property
    def value(self) -> float:
        # calculate the time since last sensor update
        passed_time = datetime.now() - self._last_update

        # check if the sensor value needs to be updated
        if passed_time.seconds >= UPDATE_INTERVAL:
            self._last_update = datetime.now()  # update timestamp of last sensor update
            self._value = self._sensor.distance  # update sensor value

        return self._value

    def __init__(self, echo_pin: int, trigger_pin: int):
        self._sensor: DistanceSensor = DistanceSensor(echo=echo_pin, trigger=trigger_pin)
        self._value: float = 0.0
        self._last_update: datetime = datetime.now()


class Distance:
    FRONT: _UltrasonicSensor = _UltrasonicSensor(_EchoPins.FRONT, _TriggerPins.FRONT)
    RIGHT: _UltrasonicSensor = _UltrasonicSensor(_EchoPins.RIGHT, _TriggerPins.RIGHT)
    REAR: _UltrasonicSensor = _UltrasonicSensor(_EchoPins.BACK, _TriggerPins.BACK)
    REAR_ANGLED: _UltrasonicSensor = _UltrasonicSensor(_EchoPins.BACK_ANGLED, _TriggerPins.BACK_ANGLED)
