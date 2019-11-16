#Use this script to control any type of pwm-controlled motor attached to the PCA9685 module.
#It allows you to send a specific pwm signal to the seperate channels of the PCA9685 module as well
#as to one of several modules by specifying a I2C-bus.

#author:   @LunaNordin
#version:  0.1(15.11.2019)

import time
import curses  #import for keyboard input
import Adafruit_PCA9685  #import of library for PCA9685-module

screen = curses.initscr()  #create new screen
curses.noecho()  #do not echo keyboard input
#in this case no cbreak is used because the user is supposed to confirm input
screen.keypad(True)  #enable special-keys

#start values for I2C communication and PCA-module connection
bus = 0
addr = 0x00
chnl = 0

def __init__(self):
  """collect information on connection and initialize I2C-link"""
  
  self.getI2Cinfo(self) #get I2C information
  pwm = Adafruit_PCA9685.PCA9685(address = addr, busnum = bus)  #create new PCA9685 object with collected data input
  self.getPCAinfo(self) #get channel information
  
  
def getI2Cinfo(self):
  """collect I2C information from user"""
  
  screen.addstr("If you want to use default I2C-values press 'y', otherwise default values are used: ")
  screen.refresh()
  answ = screen.getch()
  
  if answ == ord('y'):  #user confirms to use default values
    address = 0x40  #default I2C address
    busnum = 1 #default I2C busnumber (for Raspberry Pi's newer than model 2)
    
  elif answ != ord('y'):  #user hands over I2C information manually
    screen.addstr("Please enter the I2C-address of your PCA9685 module: ")
    screen.refresh()
    addr = screen.getch() #get I2C address from user input
  
    screen.addstr("Please enter the I2C-bus of your PCA9685 module: ")
    screen.refresh()
    bus = screen.getch()  #get I2C busnumber from user input
    
 def getPCAinfo(self):
  """get PCA channel from user"""
  
  screen.addstr("Please enter the PCA9685 channel you want to send a signal to: ")
  screen.refresh()
  chnl = screen.getch() #get PCA9685 channel from user input
