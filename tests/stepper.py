# Turns stepper motor according to user input.
# author:   @LunaNordin
# version:  3.0(30.12.2019)

import sys
from time import sleep  # sleep method used for timing of steps
import RPi.GPIO as GPIO  # RPi.GPIO for GPIO-pin control

GPIO.setwarnings(False)  # disable GPIO warnings for console convenience
GPIO.setmode(GPIO.BCM)  # GPIO instance works in broadcom-memory mode
GPIO.setup(20, GPIO.OUT)  # direction pin is an output
GPIO.setup(21, GPIO.OUT)  # step pin is an output
GPIO.setup(26, GPIO.OUT)  # sleep pin is an output


def menu():
    mode = input("Enter 'd' for distance mode and 'r' for rotation mode ('q' to exit): ")
    if mode == "q":
        sys.exit()  # end script

    direction_parameter()

    if mode == "r":
        rps = input("Please type in your rps: ")
        step_movement(rps)
    elif mode == "d":
        distance_movement()

    menu()


def calculate_delay(rps):
    '''calculates delay time used between steps according to velocity'''

    delay = (1 / (200 * float(rps))) / 2  # delay based on rounds per second
    return delay


def calculate_steps(distance):
    '''calculates steps from distance'''

    steps = distance/0.00865
    return int(steps)


def stepper_sleep(status):
    '''activates and deactivates controller in order to save energy'''

    if status == "sleep":
        GPIO.output(26, GPIO.LOW)  # put controller to sleep mode
    if status == "active":
        GPIO.output(26, GPIO.HIGH)  # activate controller


def calculate_rps(velocity, distance):
    rps = velocity/1.729
    return int(rps)


def direction_parameter():
    '''sets direction of stepper'''

    direction = input("Type 'f' for forward and 'r' for reverse: ")
    if direction == "f":
        GPIO.output(20, 0)  # direction is set to clockwise
    elif direction == "r":
        GPIO.output(20, 1)  # direction is set to counterclockwise


def step_parameter():
    '''takes step parameter from user'''

    rotations = input("Type in your number of rotations ('m' for menu): ")
    if rotations == "m":
        menu()

    steps = int(rotations)*200  # steps calculated from rotation number
    return steps


def distance_parameter():
    '''takes distance parameter from user'''

    distance = input("Type in the distance[cm] you want to drive ('m' for menu): ")
    if distance == "m":
        menu()

    return distance


def velocity_parameter():
    '''takes velocity from user'''

    velocity = input("Type the velocity[cm/s] you want to drive with: ")
    return velocity


def step_movement(rps):
    '''moves stepper provided number of steps'''

    delay = calculate_delay(rps)
    steps = step_parameter()

    move(delay, steps)

    step_movement(rps)


def distance_movement():
    ''''''

    distance = distance_parameter()
    velocity = velocity_parameter()

    rps = calculate_rps(float(velocity), distance)
    delay = calculate_delay(rps)
    steps = calculate_steps(float(distance))

    move(delay, steps)

    distance_movement()


def move(delay, steps):
    ''''''

    stepper_sleep("active")  # activate stepper
    for i in range(steps):  # loop turns stepper one round in two seconds
        GPIO.output(21, GPIO.HIGH)  # make on step
        sleep(delay)
        GPIO.output(21, GPIO.LOW)  # turn step pin low to prepare next step
        sleep(delay)
    stepper_sleep("sleep")  # put stepper to sleep


menu()
