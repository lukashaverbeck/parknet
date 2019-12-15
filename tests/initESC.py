# Script for initializing the ESC build into a picar with an activation pulse.
# Run this script before using any other PWM related ESC controls.

# author: @LunaNordin
# version: 2.0(15.11.2019)

import time
import Adafruit_PCA9685  # Import the PCA9685 module

pwm = Adafruit_PCA9685.PCA9685(address=0x40, busnum=1)  # assign I2C-address and busnumber
pwm.set_pwm_freq(50)  # setting frequency

init_pwm = 340  #digital treble zero position

print("Please make sure to disconnect your ESC from the battery.")
input = input("Press Enter to start initialization process: ")

print("\nTreble-Zero pulse is send to ESC-port...", end ="")
pwm.set_pwm(0, 0, init_pwm)  # sending activation frequency
print("done!")
print("Now power on your ESC and wait until you hear it beeping.")
time.sleep(15)  #time to turn on ESC 
