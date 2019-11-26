#Script gets user input from commandline and sets this as pwm value.
#Calculates angle from pwm with math function.

#author:	@Lunanordin
#version:	1.1(26.11.2019)


from __future__ import division
import time
import math
import Adafruit_PCA9685  #import of library for PCA9685-module

pwm = Adafruit_PCA9685.PCA9685(address=0x40, busnum=1)  #create PCA9685-object at I2C-port
pwm.set_pwm_freq(50)  #set frequency

def calc_angle(x):
 val = 0.002895*(math.pow(x,2))-2.37867*x+466.65
 return val

while True:
 pwm_val = input("Please enter your pwm value: ")  #get user input from commandline (as string)
 
 if pwm_val == "q":
   break
 
 pwm.set_pwm(0, 0, int(pwm_val))  #cast user input to integer and set pwm value
 print("Angle is: " + str(calc_angle(int(pwm_val))) + "")  #Echo user input
 
