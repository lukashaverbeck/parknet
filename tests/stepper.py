# Turns stepper motor according to user input.
# author:   @LunaNordin
# version:  2.2(27.12.2019)

import sys
from time import sleep  # sleep method used for timing of steps
import RPi.GPIO as GPIO  # RPi.GPIO for GPIO-pin control

GPIO.setwarnings(False)  # disable GPIO warnings for console convenience
GPIO.setmode(GPIO.BCM)  # GPIO instance works in broadcom-memory mode
GPIO.setup(20, GPIO.OUT)  # direction pin is an output
GPIO.setup(21, GPIO.OUT)  # step pin is an output
GPIO.setup(26, GPIO.OUT)  # sleep pin is an output


def menu():
    '''takes parameters from user and initializes movement'''

    direction = input("Type 'c' for clockwise and 'r' for counterclockwise ('q' to exit): ")
    if direction == "c":
        GPIO.output(20, 1)  # direction is set to clockwise
    elif direction == "r":
        GPIO.output(20, 0)  # direction is set to counterclockwise
    elif direction == "q":
        sys.exit()  # end script

    rps = input("Please type in your rps: ")
    delay = (1/(200*float(rps)))/2   # delay based on rounds per second

    rotations = input("Type in your number of rotations: ")
    steps = int(rotations)*200  # steps calculated from rotation number

    move(steps, delay)


def move(steps, delay):
    '''moves stepper with provided parameters'''

    stepper_sleep("active")  # activate stepper
    for i in range(steps):  # loop turns stepper one round in two seconds
        GPIO.output(21, GPIO.HIGH)  # make on step
        sleep(delay)
        GPIO.output(21, GPIO.LOW)  # turn step pin low to prepare next step
        sleep(delay)
    stepper_sleep("sleep")  # put stepper to sleep
    menu()


def stepper_sleep(status):
    '''activates and deactivates controller in order to save energy'''

    if status == "sleep":
        GPIO.output(26, GPIO.LOW)  # put controller to sleep mode
    if status == "active":
        GPIO.output(26, GPIO.HIGH)  # activate controller


menu()
