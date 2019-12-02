#This script controls a picar with keyboard input via ssh-console.
#Now working with angles.
#
#author: @LunaNordin
#version: 2.0(02.12.2019)

from __future__ import division
import time
import curses  #import for keyboard input
import math
import Adafruit_PCA9685  #import of library for PCA9685-module

screen = curses.initscr()  #create new screen
curses.noecho()  #do not echo keyboard input
curses.cbreak()  #disable return-press for input
screen.keypad(True)  #enable special-keys

pwm = Adafruit_PCA9685.PCA9685(address=0x40, busnum=1)  #create PCA9685-object at I2C-port

throttle_stop = 340    #stop acceleration
throttle_max = 355     #maximum throttle    
steering_left = 35    #steer to maximum left
steering_nutral = 0  #steer to neutral position
steering_right = -35   #steer to maximum right
pulse_freq = 50        #I2C communication frequency
pwm.set_pwm_freq(pulse_freq)  #set frequency

#make sure the car does not run away on start
current_movement = throttle_stop
current_steering = steering_nutral

def calc_angle(x):
 '''gets angle and calculates coresponding pwm value'''
 val = 0.000002*(math.pow(x,4))+0.000002*(math.pow(x,3))+0.005766*(math.pow(x,2))-(1.81281*x)+324.149
 return val

#controls:
try:
  while True:
    screen.refresh()
    char = screen.getch()  #get keyboard input
    screen.clear()
    if char == ord('q'):   #pressing q stops the script
      break
    elif char == ord('w'):                    #pressing w increases speed
      #screen.addstr("W pressed")
      if current_movement < throttle_max:
        current_movement += 1
        move = True
    elif char == ord('s'):                    #pressing s decreases speed
      #screen.addstr("S pressed")
      if current_movement > throttle_stop:    
        current_movement -= 1
        move = True
    elif char == ord('a'):                    #pressing a steers left
      #screen.addstr("A pressed")
      if current_steering < steering_left:
        current_steering += 7
        move = True
    elif char == ord('d'):                    #pressing d steers right
      #screen.addstr("D pressed")
      if current_steering > steering_right:
        current_steering -= 7
        move = True
    elif char == ord('e'):                    #pressing e returns car to start condition
      #screen.addstr("E pressed")
      current_movement = throttle_stop
      current_steering = steering_nutral
      move = True
    
    if move:                                  #move converts input to motor control
      
     pwm_calc = calc_angle(current_steering)  #calculate steering pwm value from angle
     
     pwm.set_pwm(1, 0, current_movement)    #set pwm value for ESC  
     pwm.set_pwm(0, 0, int(pwm_calc))      #set pwm value for steering motor
     
     screen.clear()
     screen.addstr("Velocity PWM: " + str(current_movement) + "[pwm]" + "         Steering angle: " + str(current_steering) + "[degree]")
     screen.refresh()
      
#leave cleanly to prevent a messed up console
finally:
  curses.nocbreak()
  screen.keypad(0)
  curses.echo()
  curses.endwin()
  


