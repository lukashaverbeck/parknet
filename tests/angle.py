#Script gets user input from commandline and sets this as pwm value.
#Calculates pwm value from angle with math function.

#author:  @Lunanordin
#version:  2.0(02.12.2019)


from __future__ import division
import time
import math	#math is used to define function
import Adafruit_PCA9685  #import of library for PCA9685-module

pwm = Adafruit_PCA9685.PCA9685(address=0x40, busnum=1)  #create PCA9685-object at I2C-port
pwm.set_pwm_freq(50)  #set frequency

def calc_angle(x):
 '''gets angle and calculates coresponding pwm value'''
 val = 0.000002*(math.pow(x,4))+0.000002*(math.pow(x,3))+0.005766*(math.pow(x,2))-(1.81281*x)+324.149
 return val

while True:
 pwm_val = input("Please enter your angle: ")  #get user input from commandline (as string)
 
 if pwm_val == "q":	#if user types "q" end the program
   break
 
 pwm_calc = calc_angle(int(pwm_val))	#a pwm vale is calculated from user input
 
 pwm.set_pwm(0, 0, int(pwm_calc))  #cast pwm value to integer and set it on pwm object
 print("pwm value is: " + str(pwm_calc) + "")  #Echo user input
 
