# This script controls a picar with keyboard input via ssh-console.
#
# author: @LunaNordin
# version: 4.0(29.12.2019)

import curses  # import for keyboard input
import math  # math for calculating functions
import Adafruit_PCA9685  # import of library for PCA9685-module
from time import sleep
import threading
import ctypes
import RPi.GPIO as GPIO  # RPi.GPIO for GPIO-pin control

screen = curses.initscr()  # create new screen
curses.noecho()  # do not echo keyboard input
curses.cbreak()  # disable return-press for input
screen.keypad(True)  # enable special-keys

GPIO.setwarnings(False)  # disable GPIO warnings for console convenience
GPIO.setmode(GPIO.BCM)  # GPIO instance works in broadcom-memory mode
GPIO.setup(21, GPIO.OUT)  # step pin is an output

pwm = Adafruit_PCA9685.PCA9685(address=0x40, busnum=1)  # create PCA9685-object at I2C-port

steering_left = 35  # steer to maximum left
steering_neutral = 0  # steer to neutral position
steering_right = -35  # steer to maximum right
pulse_freq = 50  # I2C communication frequency
pwm.set_pwm_freq(pulse_freq)  # set frequency

# make sure the car does not run away on start
current_rps = 0
current_steering = steering_neutral


def calc_angle(x):
    '''gets angle and calculates coresponding pwm value'''
    val = 0.000002 * (math.pow(x, 4)) + 0.000002 * (math.pow(x, 3)) + 0.005766 * (math.pow(x, 2)) - (
                1.81281 * x) + 324.149
    return val


def move_stepper(delay):
    if delay != 0:
        try:
            while True:
                sleep(1)  # wait to keep rps
                print(test)
        finally:
            pass


# controls:
try:
    delay = 0
    t = threading.Thread(target=move_stepper, args=(delay,))
    t.start()
    while True:
        screen.refresh()
        char = screen.getch()  # get keyboard input
        screen.clear()
        if char == ord('q'):  # pressing q stops the script
            t = None
            break
        elif char == ord('w'):  # pressing w increases speed
            # screen.addstr("W pressed")
            if current_rps < 5:
                current_rps += 1
                move = True
        elif char == ord('s'):  # pressing s decreases speed
            # screen.addstr("S pressed")
            if current_rps > 0:
                current_rps -= 1
            move = True
        elif char == ord('a'):  # pressing a steers left
            # screen.addstr("A pressed")
            if current_steering < steering_left:
                current_steering += 7
                move = True
        elif char == ord('d'):  # pressing d steers right
            # screen.addstr("D pressed")
            if current_steering > steering_right:
                current_steering -= 7
                move = True
        elif char == ord('e'):  # pressing e returns car to start condition
            # screen.addstr("E pressed")
            current_rps = 0
            current_steering = steering_neutral
            move = True

        if move:  # move converts input to motor controls

            pwm_calc = calc_angle(current_steering)  # calculate steering pwm value from angle
            pwm.set_pwm(0, 0, int(pwm_calc))  # set pwm value for steering motor

            if current_rps > 0:
                delay = (1 / (200 * float(current_rps))) / 2  # delay based on rounds per second
            elif current_rps == 0:
                delay = 0

            t.join()

            screen.clear()
            screen.addstr("Velocity: " + str(current_rps) + "[rps]" + "         Steering angle: " + str(current_steering) + "[degree]")
            screen.refresh()

# leave cleanly to prevent a messed up console
finally:
    curses.nocbreak()
    screen.keypad(0)
    curses.echo()
    curses.endwin()
