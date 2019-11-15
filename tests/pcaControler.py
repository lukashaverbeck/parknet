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

bus = 0
addr = 0x00
chnl = 0

def __init__(self):
  self.getI2Cinfo(self)
  pwm = Adafruit_PCA9685.PCA9685(address = addr, busnum = bus)
  self.getPCAinfo(self)
  
  
def getI2Cinfo(self):
  screen.addstr("If you want to use default I2C-values press 'y', otherwise default values are used: ")
  screen.refresh()
  answ = screen.getch()
  if answ == ord('y'):
    address = 0x40
    busnum = 1
  elif answ != ord('y'):
    screen.addstr("Please enter the I2C-address of your PCA9685 module: ")
    screen.refresh()
    addr = screen.getch()
  
    screen.addstr("Please enter the I2C-bus of your PCA9685 module: ")
    screen.refresh()
    bus = screen.getch()
    
 def getPCAinfo(self):
  screen.addstr("Please enter the PCA9685 channel you want to send a signal to: ")
  screen.refresh()
  chnl = screen.getch()
