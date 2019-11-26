#Script gets user input from commandline and sets this as pwm value for steering servo.
#author:    @Lunanordin
#version:   1.0(26.11.2019)


from __future__ import division
import time
import Adafruit_PCA9685  #import of library for PCA9685-module

pwm = Adafruit_PCA9685.PCA9685(address=0x40, busnum=1)  #create PCA9685-object at I2C-port
pwm.set_pwm_freq(50)  #set frequency


while True:
 pwm_val = input("Please enter your pwm value: ")  #get user input from commandline (as string)
 
 pwm.set_pwm(0, 0, int(pwm_val))  #cast user input to integer and set pwm value
 print("Set steering motor to: " + str(pwm_val) + "pwm.")  #Echo user input
