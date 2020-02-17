# This script calculates the distance between an HC-SR04 module and the nearest object.
# It is capable of handling multiple modules simultaneously.
#
# version: 1.0 (30.12.2019)

import RPi.GPIO as GPIO
import time
import curses  # keyboard input and interface

screen = curses.initscr()  # create new screen
screen.nodelay(True)  # .getch() is ignored if no keyboard input is detected
curses.noecho()  # do not ECHO_1 keyboard input
curses.cbreak()  # disable return-press for input
screen.keypad(True)  # enable special-keys

GPIO.setmode(GPIO.BCM)  # set GPIO mode

TRIG_1 = 18  # trigger pin of HC-SR04 module(front)
TRIG_2 = 23  # trigger pin of HC-SR04 module(side)
TRIG_3 = 25   # trigger pin of HC-SR04 module(back)
TRIG_4 = 24  # trigger pin of HC-SR04 module(back-angled)
ECHO_1 = 4  # echo pin of HC-SR04 module(front)
ECHO_2 = 17  # echo pin of HC-SR04 module(side)
ECHO_3 = 22  # echo pin of HC-SR04 module(back)
ECHO_4 = 27  # echo pin of HC-SR04 module(back-angled)

# define all trigger pins as outputs and all echo pins as inputs
# make sure all pins ar free to use to avoid data collision
GPIO.setup(TRIG_1, GPIO.OUT)
GPIO.setup(ECHO_1, GPIO.IN)
GPIO.setup(TRIG_2, GPIO.OUT)
GPIO.setup(ECHO_2, GPIO.IN)
GPIO.setup(TRIG_3, GPIO.OUT)
GPIO.setup(ECHO_3, GPIO.IN)
GPIO.setup(TRIG_4, GPIO.OUT)
GPIO.setup(ECHO_4, GPIO.IN)


def measure_distance(trigpin, echopin):
    """ gets distance value from the module with the reported pins

        Args:
            trigpin (int): pin sending the signal
            echopin (int): pin sending the signal

        Returns:
            float: measured distance in cm rounded to two decimal places
    """

    GPIO.output(trigpin, True)  # activate the trigger channel of HC-SR04 module
    time.sleep(0.00001)  # 10µs activate 8 ultrasound bursts at 40 kHz
    GPIO.output(trigpin, False)  # deactivate trigger channel

    while GPIO.input(echopin) == 0:  # measure time in which echo signal is detected
        pulse_start = time.time()

    while GPIO.input(echopin) == 1:  # measure the time of the echo signal
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start  # time it took the signal to hit the object and return to sensor
    distance = pulse_duration * 17150  # calculate into cm 34300[cm/s]=Distance[cm]/(Time[s]/2)
    distance = round(distance, 2)
    
    return distance


GPIO.output(TRIG_1, False)  # pull down trigger pin in case the pin is still activated
screen.addstr("Waiting For Sensor To Settle")
screen.refresh()  # making an output during waiting time
time.sleep(2)  # wait two seconds to make sure there are no signal fragments which could be detected
screen.clear()  # clear the output area

# cycle with sensordetection
while True:
    char = screen.getch()  # get keyboard input
    if char == ord('q'):  # stop script when the q key is pressed
        break

    distance_1 = measure_distance(TRIG_1, ECHO_1)  # call sensordetection function for front module
    distance_2 = measure_distance(TRIG_2, ECHO_2)  # call sensordetection function for side module
    distance_3 = measure_distance(TRIG_3, ECHO_3)  # call sensordetection function for back module
    distance_4 = measure_distance(TRIG_4, ECHO_4)  # call sensordetection function for back module

    screen.clear()  # clear screen for next output

    # sho results in the console
    screen.addstr("Distance_front:        {distance_1} cm\n")
    screen.addstr("Distance_side:         {distance_2} cm\n")
    screen.addstr("Distance_back:         {distance_3} cm\n")
    screen.addstr("Distance_back(angled): {distance_4} cm")
    screen.refresh()

# in order to not mess up the console all setting need to be reset to default values
GPIO.cleanup()
curses.nocbreak()
screen.keypad(0)
curses.echo()
curses.endwin()
