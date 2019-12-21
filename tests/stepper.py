# drives a bi-polar stepper motor
# author:   @LunaNordin
# version:  1.0(21.12.2019)

from time import sleep
import RPi.GPIO as GPIO

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(20, GPIO.OUT)
GPIO.setup(21, GPIO.OUT)

GPIO.output(20, 1)

delay = 0.005
for i in range(200):
    GPIO.output(21, GPIO.HIGH)
    sleep(delay)
    GPIO.output(21, GPIO.LOW)
    sleep(delay)
