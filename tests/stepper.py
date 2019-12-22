# Turns stepper motor according to user input.
# author:   @LunaNordin
# version:  2.0(22.12.2019)

from time import sleep  # sleep method used for timing of steps
import RPi.GPIO as GPIO  # RPi.GPIO for GPIO-pin control

GPIO.setwarnings(False)  # disable GPIO warnings for console convenience
GPIO.setmode(GPIO.BCM)  # GPIO instance works in broadcom-memory mode
GPIO.setup(20, GPIO.OUT)  # direction pin is an output
GPIO.setup(21, GPIO.OUT)  # step pin is an output

GPIO.output(20, 1)  # direction is set to clockwise

delay = 0.005   # delay based on step count
for i in range(200):  # loop turns stepper one round in two seconds
    GPIO.output(21, GPIO.HIGH)  # make on step
    sleep(delay)
    GPIO.output(21, GPIO.LOW)  # turn step pin low to prepare next step
    sleep(delay)
