# This script tests the relation between pwm and steering angles or velocities.
# It gets user inputs and calculates the corresponding pwm values.
# 
# NOTE This script is based on angle.py version: 2.0 (30.12.2019)
# 
# version:  1.0 (13.12.2019)

import sys
import time
import math  # math is used for calculating with functions
import Adafruit_PCA9685  # import of library for PCA9685-module


mode = ""  # global value for mode chosen by user

pwm = Adafruit_PCA9685.PCA9685(address=0x40, busnum=1)  # create PCA9685-object at I2C-port
pwm.set_pwm_freq(50)  # set frequency


def setup():
    """ can be seen as 'home menu'"""

    global mode

    # change mode based on user input
    mode = input("To set a steering angle please press 'a'\nIn order to set a velocity press 'v'" + '\n' + "Press 'r' to return to start menu\nPress 'q' to quit:     ")
    
    if mode == "q":  # stop script when the q key is pressed
        sys.exit()
    elif mode == "a" or mode == "v":  # pass this in case mode is nonsense
        input_value()
    
    setup()  # restart "home menu"


def calc_steering_pwm(angle):
    """ calculates a pwm value for a given angle

        Args:
            angle (float): angle to be converted to a pwm value

        Returns:
            float: corresponding pwm value
    """

    return 2e-6 * angle ** 4 + 2e-6 * angle ** 3 + .005766 * angle ** 2 - 1.81281 * angle + 324.149


def calc_velocity_pwm(velocity):
    """ calculates a pwm value from velocity
        NOTE this function does not work yet
        TODO implement function

        Args:
            velocity (float): velocity to be converted to a pmw value

        Returns:
            float: corresponding pwm value
    """

    return velocity


def input_value():
    """ uses user input to set values according to mode """

    global mode
 
    # repeat until user quits
    while True:
        if mode == "a":  # user wants to set steering angle
            user_input = input("\nPlease enter your angle[degree]: ")

            if user_input == "q":  # stop script when the q key is pressed
                sys.exit()
            elif user_input == "r":  # return to "home menu"
                setup()
            elif user_input == "e":  # emergency stop option
                pwm.set_pwm(0, 0, 325)  # set steering neutral
                pwm.set_pwm(1, 0, 340)  # set esc to zero
                print("Emergency stopped vehicle!")
                input_value()  # restart input method

            input_int = int(user_input)  # cast user input to int for further processing

            if 35 >= input_int >= -35:  # check if input is in range
                pwm_calc = calc_steering_pwm(input_int)   # calculate pwm from angle
                pwm.set_pwm(0, 0, int(pwm_calc))  # cast calculated value to integer and set as pwm value
                print(f"pwm value is: {pwm_calc}")  # echo for user and repeat
            else:
                # warn user and repreat                
                print("Your angle is out of range! Please use angle between 35 and -35 degrees.")

        elif mode == "v":  # user wants to set velocity
            user_input = input("'\n'Please enter your velocity[m/s]: ")
    
            if user_input == "q":  # stop script when the q key is pressed
                sys.exit()
            elif user_input == "r":  # return to "home menu"
                setup()
            elif user_input == "e":  # emergency stop option
                pwm.set_pwm(0, 0, 325)  # set steering neutral
                pwm.set_pwm(1, 0, 340)  # set esc to zero
                print("Emergency stopped vehicle!")
                input_value()  # restart input method
    
            input_int = int(user_input)  # cast user input into int for further processing

            pwm_calc = calc_velocity_pwm(input_int)  # returns untouched input for now
            pwm.set_pwm(0, 0, int(pwm_calc))  # cast calculated value to integer and set as pwm value
            print(f"pwm value is: {pwm_calc}")  # echo for user and repeat


setup()  # start the script
