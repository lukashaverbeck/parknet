#Script for testing relation between pwm and steering or velocity.
#Gets user input and calculates pwm values based on determined function.

#NOTICE: This script is based on angle.py version: 2.0(01.12.2019) 

#author:   @Lunanordin
#version:  1.0(03.12.2019)  

import sys
import time
import math  #math is used for calculating with functions
import Adafruit_PCA9685  #import of library for PCA9685-module

__mode = ""  #global value for mode chosen by user

pwm = Adafruit_PCA9685.PCA9685(address=0x40, busnum=1)  #create PCA9685-object at I2C-port
pwm.set_pwm_freq(50)  #set frequency

def setup():
  '''can be seen as "home menu"'''
  global __mode  #import global value
  __mode = input("To set a steering angle please press 'a'" + '\n' + "In order to set a velocity press 'v'" + '\n' + "Press 'r' to return to start menu" + '\n' + "Press 'q' to quit:     ")  #change mode based on user input
  if __mode == "q":  #exit if mode is set to "q"
    sys.exit()
  elif __mode == "a" or "v":  #pass this in case mode is nonsense
    input_value()
    
  setup()  #restart "home menu"
  
def calc_steering_pwm(x):
 '''calculates a pwm value from angle'''
 val = 0.000002*(math.pow(x,4))+0.000002*(math.pow(x,3))+0.005766*(math.pow(x,2))-(1.81281*x)+324.149  #function developed from measurements
 return val
 
def calc_velocity_pwm(x):
 '''calculates a pwm value from velocity'''
 val = x  #function is missing yet
 return val  #pwm value is returned unchanged
  
def input_value():
 '''uses user input to set values according to mode'''
 global __mode  #import global value
 
 while True:  #repeat until user quits
  if __mode == "a":  #user wants to set steering angle
    user_input = input('\n' + "Please enter your angle[degree]: ")  #get user input from commandline (as string)
    
    if user_input == "q":  #exit if input is "q"
      sys.exit()
    elif user_input == "r":  #return to "home menu"
      setup()
    
    input_int = int(user_input)  #cast user input into int for further processing
    
    if input_int <= 35 and input_int >= -35:  #check if input is in range   
     pwm_calc = calc_steering_pwm(input_int)   #calculate pwm from angle
     pwm.set_pwm(0, 0, int(pwm_calc))  #cast calculated value to integer and set as pwm value
     print("pwm value is: " + str(pwm_calc) + "")  #echo for user and repeat
    elif input_int <= -35 or input_int >= 35:  #if input is not in range
      print("Your angle is out of range! Please use angle between 35 and -35 degrees.")  #tell user and repeat    
    
  if __mode == "v":  #user wants to set velocity
    user_input = input('\n' + "Please enter your velocity[m/s]: ")  #get user input from commandline (as string)
    
    if user_input == "q":  #exit if input is "q"
      sys.exit()
    elif user_input == "r":  #return to "home menu"
      setup()
    
    input_int = int(user_input)  #cast user input into int for further processing
    
    pwm_calc = calc_velocity_pwm(input_int)  #returns untuched input for now    
    pwm.set_pwm(0, 0, int(pwm_calc))  #cast calculated value to integer and set as pwm value
    print("pwm value is: " + str(pwm_calc) + "")  #echo for user and repeat

setup()  #start the script