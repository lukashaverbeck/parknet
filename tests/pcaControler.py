#Use this script to control any type of pwm-controlled motor attached to the PCA9685 module.
#It allows you to send a specific pwm signal to the seperate channels of the PCA9685 module as well
#as to one of several modules by specifying a I2C-bus.

#author:   @LunaNordin
#version:  1.0(17.11.2019)

import sys
import time
import curses  #import for keyboard input
import Adafruit_PCA9685  #import of library for PCA9685-module

screen = curses.initscr()  #create new screen
curses.echo()  #do not echo keyboard input
curses.cbreak()  #in this case no cbreak is used because the user is supposed to confirm input
screen.keypad(True)  #enable special-keys

#start values for I2C communication and PCA-module connection
pwm = 0
bus = 0
addr = 0x00
chnl = 0

class Controller:
 
 def __init__(self):
   """collect information on connection and initialize I2C-link"""
   
   self.getI2Cinfo() #get I2C information
   self.pwm = Adafruit_PCA9685.PCA9685(address = self.addr, busnum = self.bus)  #create new PCA9685 object with collected data input
   self.getPCAinfo() #get channel information
   self.sendSignal()
 
 
 def getI2Cinfo(self):
    """collect I2C information from user"""
    screen.clear()
    screen.addstr("If you want to use default I2C-values press 'y', otherwise default values are used: ")
    screen.refresh()
    answ = screen.getch()
    
    if answ == ord('y'):  #user confirms to use default values
      self.addr = 0x40  #default I2C address
      self.bus = 1 #default I2C busnumber (for Raspberry Pi's newer than model 2)
      
    elif answ != ord('y'):  #user hands over I2C information manually
      screen.addstr("Please enter the I2C-address of your PCA9685 module: ")
      screen.refresh()
      self.addr = screen.getch() #get I2C address from user input
    
      screen.addstr("Please enter the I2C-bus of your PCA9685 module: ")
      screen.refresh()
      self.bus = screen.getch()  #get I2C busnumber from user input
     
 
 def getPCAinfo(self):
  """get PCA channel from user"""
  screen.clear()
  screen.addstr("Please enter the PCA9685 channel you want to send a signal to: ")
  screen.refresh()
  val1 = screen.getkey()
  val2 = screen.getkey()
  val0 = val1 + val2
  try:
    chnl = int(val0)
    if chnl < 0 or chnl > 15:
      screen.clear()
      screen.addstr("Not a valid channel. Ending program.")
      screen.refresh()
      time.sleep(2)
      self.end()
    self.chnl = chnl
  except:
    screen.clear()
    screen.addstr("Not a valid channel. Ending program.")
    screen.refresh()
    time.sleep(2)
    self.end()
 
 
 def sendSignal(self):
   screen.clear()
   screen.addstr("Please enter your pwm value: ")
   screen.refresh()
   while True:
     val1 = screen.getkey()
     if val1 == "q":
       self.end()
       break
     val2 = screen.getkey()
     val3 = screen.getkey()
     val0 = val1 + val2 + val3
     try:
      val = int(val0)
      
      screen.clear()
      screen.addstr(str(self.chnl) + "    " + str(val))
      screen.refresh()
      time.sleep(2)
      
      self.pwm.set_pwm(self.chnl, 0, val)
      screen.clear()
      screen.addstr("Curent value is " + str(val) + ". Please enter your new pwm value: ")
      screen.refresh()
     except:
       screen.clear()
       screen.addstr("Input is not a valid pwm value! Please enter a valid pwm value: ")
       screen.refresh()
       time.sleep(3)
     
     
 def end(self):
   curses.nocbreak()
   screen.keypad(0)
   curses.echo()
   curses.endwin()
   sys.exit()
    
cntrl = Controller()
