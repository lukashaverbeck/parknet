# Script gets user input from commandline and sets this as pwm value.
# Calculates the pwm value from an angle with a mathematical function.
#
# author:  @Lunanordin
# version:  2.0 (30.12.2019)


from __future__ import division
import time
import Adafruit_PCA9685  # library for PCA9685-module

pwm = Adafruit_PCA9685.PCA9685(address=0x40, busnum=1)  # create PCA9685 object at I2C-port
pwm.set_pwm_freq(50)

def calc_angle(angle):
    """ calculates a pwm value for a given angle

        Args:
            angle (float): angle to be converted to a pwm value

        Returns:
            float: corresponding pwm value    
    """

    return 2e-6 * angle ** 4 + 2e-6 * angle ** 3 + .005766 * angle ** 2 - 1.81281 * angle + 324.149


while True:
    pwm_val = input("Please enter your angle: ")  # get user input from commandline (as string)
    
    if pwm_val == "q": break  # stop script when the q key is pressed
    
    pwm_calc = calc_angle(int(pwm_val))	 # get pwm value for user input
    pwm.set_pwm(0, 0, int(pwm_calc))  # cast pwm value to integer and set it on pwm object
    print(f"pwm value is: {pwm_calc}")  # echo user input
 
