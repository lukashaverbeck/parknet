# Turns stepper motor according to user input.
# Determines length corresponding with one step.
# author:   @LunaNordin
# version:  2.3(28.12.2019)

import sys
from time import sleep  # sleep method used for timing of steps
import RPi.GPIO as GPIO  # RPi.GPIO for GPIO-pin control

GPIO.setwarnings(False)  # disable GPIO warnings for console convenience
GPIO.setmode(GPIO.BCM)  # GPIO instance works in broadcom-memory mode
GPIO.setup(20, GPIO.OUT)  # direction pin is an output
GPIO.setup(21, GPIO.OUT)  # step pin is an output
GPIO.setup(26, GPIO.OUT)  # sleep pin is an output


def menu():
    '''main menu used to choose mode and set shared parameters'''

    mode = input("Enter 'c' for calibration mode and 's' for single movement ('q' to exit): ")
    if mode == "q":
        sys.exit()  # end script

    direction = input("Type 'c' for clockwise and 'r' for counterclockwise: ")
    if direction == "c":
        GPIO.output(20, 1)  # direction is set to clockwise
    elif direction == "r":
        GPIO.output(20, 0)  # direction is set to counterclockwise

    rps = input("Please type in your rps: ")
    delay = (1 / (200 * float(rps))) / 2  # delay based on rounds per second

    if mode == "s":
        parameters(delay)  # driving based on user parameters
    elif mode == "c":
        count_steps(delay)  # determine step length

    menu()  # if input is invalid start over main menu


def parameters(delay):
    '''takes parameters from user and initializes movement'''

    rotations = input("Type in your number of rotations ('m' for menu): ")
    if rotations == "m":
        menu()  # return to main menu

    steps = int(rotations)*200  # steps calculated from rotation number
    move(steps, delay)  # move stepper


def move(steps, delay):
    '''moves stepper with provided parameters'''

    stepper_sleep("active")  # activate stepper
    for i in range(steps):  # loop turns stepper one round in two seconds
        GPIO.output(21, GPIO.HIGH)  # make one step
        sleep(delay)  # wait to keep rps
        GPIO.output(21, GPIO.LOW)  # turn step pin low to prepare next step
        sleep(delay)  # wait to keep rps
    stepper_sleep("sleep")  # put stepper to sleep
    parameters(delay)  # get new parameters from user


def stepper_sleep(status):
    '''activates and deactivates controller in order to save energy'''

    if status == "sleep":
        GPIO.output(26, GPIO.LOW)  # put controller to sleep mode
    if status == "active":
        GPIO.output(26, GPIO.HIGH)  # activate controller


def count_steps(delay):
    '''runs motor until user stops it and counts steps to determine length of one step'''

    print("Enter 'e' to stop vehicle: ")
    print(delay)
    rotations = 0  # start value of rotation number
    stop = False  # parameter to end the loop
    stepper_sleep("active")  # activate stepper
    while not stop:  # until user stops car
        GPIO.output(21, GPIO.HIGH)  # make one step
        sleep(delay)  # wait to keep rps
        GPIO.output(21, GPIO.LOW)  # turn step pin low to prepare next step
        sleep(delay)  # wait to keep rps
        rotations += 1  # increase step counter
    stepper_sleep("sleep")  # put stepper to sleep
    menu()  # return to main menu


menu()  # start script with main menu
