from __future__ import annotations

import time
from typing import Tuple, Callable, Optional, Union

import Adafruit_PCA9685
from RpiMotorLib import RpiMotorLib

import attributes
import sensing
import util

_MIN_ANGLE: float = -20
_MAX_ANGLE: float = 20

_STEP_UNIT: int = 80  # number of steps to do at a time
_DISTANCE_PER_STEP: float = 0.0125  # movement in mm per step TODO: check if value is correct
_MOTOR_TYPE: str = "DRV8825"


class _Pins:
    DIRECTION: int = 20
    STEP: int = 21
    MODE: Tuple[int, int, int] = (24, 25, 26)  # TODO: check if values are correct


class Direction:
    FORWARD: int = 0
    BACKWARD: int = 1


_Direction: type = Union[Direction.FORWARD, Direction.BACKWARD]
_DrivingMotor: type = RpiMotorLib.A4988Nema
_SteeringMotor: type = Adafruit_PCA9685.PCA9685


def _calculate_angle_pwm(angle: float) -> float:
    """ Converts a steering angle to a pulse width modulation (PWM) value to address the steering motor accordingly.

    Notes:
        The parameters for the PWM approximation function defined as agent attributes must be in descending exponential
        order (k0 * x^(n-1) + k1 * x^(n-2) + ... + kn).

    Args:
      angle: Angle in degrees to be converted to PWM.

    Returns:
        The PWM value for the steering angle.
    """

    # get steering parameters in reversed order -> k0, ..., kn
    coefficients = reversed(attributes.STEERING_PARAMETERS)

    # sum up polynomial approximation of the pwm value -> k0 * x^0 + ... kn * x^(n-1)
    return sum(coefficient * (angle ** exponent) for exponent, coefficient in enumerate(coefficients))


@util.SingleUse
class Driver:
    @property
    def forward(self) -> _Mode:
        return self._mode(Direction.FORWARD)

    @property
    def backward(self) -> _Mode:
        return self._mode(Direction.BACKWARD)

    def __init__(self):
        # TODO: factor out magic numbers
        self.steering_motor: _SteeringMotor = Adafruit_PCA9685.PCA9685(address=0x40, busnum=1)
        self.steering_motor.set_pwm_freq(50)
        self._driving_motor: _DrivingMotor = RpiMotorLib.A4988Nema(_Pins.DIRECTION, _Pins.STEP, _Pins.MODE, _MOTOR_TYPE)

        self._current_mode: Optional[_Mode] = None

    # TODO: add documentation
    def _mode(self, direction: _Direction) -> _Mode:
        """ Creates a new driving mode.

        In order to ensure that at any time at maximum one driving mode is executed, the current driving mode is stopped
        in the case that there is one. The current mode is then updated and the new one returned.

        Args:
            direction: Direction to drive in (either forward or backward).

        Returns:
            The corresponding driving mode.
        """

        # abort current driving mode if it exists
        if self._current_mode is not None:
            self._current_mode.stop()

        # set and return new driving mode
        self._current_mode = _Mode(self._driving_motor, direction)
        return self._current_mode

    def steer(self, angle: float) -> None:
        """ Changes the steering angle of the vehicle.

        The given angle is translated to a PWM value which is then transmitted to the steering motor. It is ensured that
        the steering angle is within the defined boundaries.

        Args:
            angle: Desired steering angle in degrees.
        """

        # ensure that angle is within boundaries
        angle = max(_MIN_ANGLE, min(_MAX_ANGLE, angle))

        # calculate and set pwm value
        pwm = _calculate_angle_pwm(angle)
        self.steering_motor.set_pwm(0, 0, pwm)  # TODO: factor out magic numbers


class _Mode:
    def __init__(self, driving_motor: _DrivingMotor, direction: _Direction):
        self._active: bool = True
        self._driving_motor: _DrivingMotor = driving_motor
        self._forward: direction = self._forward == Direction.FORWARD

    # TODO: add option for maximum distance and maximum duration
    def do_while(self, condition: Callable[[], bool]) -> None:
        """ Drives as long as the mode is active and the given condition is met.

        Args:
            condition: Function defining the condition.
        """

        while self._active and condition():
            self._go(_STEP_UNIT)

    def do_for(self, distance: float) -> None:
        """ Drives a given distance.

        Args:
            distance: Distance to drive (in mm).
        """

        # calculate number of steps corresponding to the distance.
        steps = int(round(_STEP_UNIT * distance, 0))
        self._go(steps)

    def _go(self, steps: int) -> None:
        """ Addresses the driving motor to drive a given number of steps.

        Args:
            steps: Number of steps to drive.
        """

        # divide steps into single step units and execute them separately
        while self._active and steps >= _STEP_UNIT:
            # if possible, drive for a single step unit and decrement the remaining number of steps accordingly
            if self._movement_possible(_STEP_UNIT):
                self._driving_motor.motor_go(clockwise=self._forward, steps=_STEP_UNIT)
                steps -= _STEP_UNIT
            # otherwise wait for the distances to change
            else:
                time.sleep(1)

        # if possible, drive remaining number of steps
        if self._movement_possible(steps):
            self._driving_motor.motor_go(clockwise=self._forward, steps=steps)

    def _movement_possible(self, steps: int) -> bool:
        """ Determines whether the driver may move by a given number of steps.

        This is exactly the case if the mode is currently active and the movement would not lead to undercutting the
        minimum safety distance which must always be maintained. The safety distance is checked for the direction of the
        movement (either front or rear).

        Args:
            steps: Number of steps to drive.

        Returns:
            Whether the driver may drive the given number of steps.
        """

        # if the mode is no longer active, no movement is allowed as to prevent simultaneous movements
        if not self._active:
            return False

        # get ultrasonic distance sensor corresponding to the direction
        sensor = sensing.Distance.FRONT if self._forward else sensing.Distance.REAR

        # predict the distance for after driving for a given number of steps
        predicted_distance = sensor.value - _DISTANCE_PER_STEP * steps

        # return whether safety distances can be maintained
        return predicted_distance >= util.const.Driving.SAFETY_DISTANCE

    def stop(self) -> None:
        """ Deactivates the mode by flagging it as inactive.

        It is possible that current movements stop only after a short delay as they cannot be aborted directly. Instead,
        further movements are no longer executed. For this reason every movement is divided into short movement
        sequences.
        """

        self._active = False
