# Script for initilizing the ESC build into a picar with an activation pulse.
# Run this script before using any other PWM related ESC controls.

# author: @LunaNordin
# version: 1.0(03.11.2019)

from __future__ import division

import time
import Adafruit_PCA9685  # Import the PCA9685 module

pwm = Adafruit_PCA9685.PCA9685(address=0x40, busnum=1)  #assign I2C-address and busnumber


servo_min = 340  #pwm-value to stop motor
servo_act = 330  #pwm-value necessary to activate ESC

pulse_freq = 50  #communication frequency
pwm.set_pwm_freq(pulse_freq)  #setting frequency
channel = 1      #channel number of ESC at PCA9685

print('WARNING:  To prevent a runaway-scenario please lift your car off the ground!')
time.sleep(5)

print('Initializing ESC with activation pulse (2000ms on 330 at 50Hz)...')

pwm.set_pwm(channel, 0, servo_act)  #sending activation frequency
time.sleep(2)                       #wait two seconds to make sure ESC responds
pwm.set_pwm(channel, 0, servo_min)  #turning down motor spin
time.sleep(2)                       #wait two seconds to make sure ESC responds
