# This script rotates the stepper motor accordingly to user input.
#
# version: 1.0 (31.12.2019)

import sys
from time import sleep
import RPi.GPIO as GPIO

GPIO.setwarnings(False)  # disable GPIO warnings for console convenience
GPIO.setmode(GPIO.BCM)  # GPIO instance works in broadcom-memory mode
GPIO.setup(20, GPIO.OUT)  # direction pin is an output
GPIO.setup(21, GPIO.OUT)  # step pin is an output
GPIO.setup(26, GPIO.OUT)  # sleep pin is an output


def menu():
    """ main menu lets user chose driving mode """

    mode = input("Enter 'd' for distance mode and 'r' for rotation mode ('q' to exit): ")
    if mode == "q": sys.exit()  # stop script when the q key is pressed

    direction_parameter()  # set direction

    if mode == "r":
        rps = input("Please type in your rps: ")
        step_movement(rps)  # activate driving with stepper parameters
    elif mode == "d":
        distance_movement()  # activate driving with distance parameters

    menu()  # if there is no valid user input return to main menu


def stepper_sleep(status):
    """ activates and deactivates controller in order to save energy

        Args:
            status (str): motor status (sleep or active)
    """

    if status == "sleep":
        GPIO.output(26, GPIO.LOW)  # put controller to sleep mode
    if status == "active":
        GPIO.output(26, GPIO.HIGH)  # activate controller


def calculate_delay(rps):
    """ calculates delay time used between steps according to velocity

        Args:
            rps (float): rounds per second

        Returns:
            float: calculated delay time
    """

    delay = (1 / (200 * float(rps))) / 2  # delay based on rounds per second
    return delay


def calculate_steps(distance):
    """ calculates steps from distance
    
        Args:
            distance (float): distance in cm to be converted to steps

        Returns:
            int: corresponding number of steps
    """

    steps = distance / 0.00865  # one step is about 0.00865cm
    return int(steps)


def calculate_rps(velocity, distance):
    rps = velocity / 1.729
    return int(rps)


def direction_parameter():
    """ sets direction of stepper """

    direction = input("Type 'f' for forward and 'r' for reverse: ")
    if direction == "f":
        GPIO.output(20, 0)  # direction is set to clockwise
    elif direction == "r":
        GPIO.output(20, 1)  # direction is set to counterclockwise


def rotation_parameter():
    """ takes rotation parameter from user """

    rotations = input("Type in your number of rotations ('m' for menu): ")
    if rotations == "m":
        menu()  # return to main menu

    steps = int(rotations) * 200  # steps calculated from rotation number(one rotation is 200 steps)
    return steps


def distance_parameter():
    """ takes distance parameter from user """

    distance = input("Type in the distance[cm] you want to drive ('m' for menu): ")
    if distance == "m":
        menu()  # return to main menu
    return distance


def velocity_parameter():
    """ takes velocity from user """

    velocity = input("Type the velocity[cm/s] you want to drive with: ")
    return velocity


def step_movement(rps):
    """ moves stepper provided number of steps with provided rps """

    delay = calculate_delay(rps)
    steps = rotation_parameter()  # get number of steps from user

    move(delay, steps)  # move stepper
    step_movement(rps)  # ask for rotation parameter and move again


def distance_movement():
    """ move stepper provided distance with provided velocity """

    distance = distance_parameter()  # get distance from user
    velocity = velocity_parameter()  # get velocity from user

    rps = calculate_rps(float(velocity), distance)  # convert velocity to rps
    delay = calculate_delay(rps)  # calculate delay
    steps = calculate_steps(float(distance))  # convert distance to steps

    move(delay, steps)  # move stepper
    distance_movement()  # ask for new parameters and move again


def move(delay, steps):
    """ moves stepper """

    stepper_sleep("active")  # activate stepper
    for i in range(steps):  # loop turns stepper one round in two seconds
        GPIO.output(21, GPIO.HIGH)  # make on step
        sleep(delay)
        GPIO.output(21, GPIO.LOW)  # turn step pin low to prepare next step
        sleep(delay)
    stepper_sleep("sleep")  # put stepper to sleep


menu()  # start main menu when script is started
