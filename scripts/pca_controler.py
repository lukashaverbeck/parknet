# This script is used  to control any type of pwm-controlled hardware attached to the PCA9685 module.
# It allows to send a specific pwm signal to the seperate channels of the
# PCA9685 module as well as to one of several modules by specifying a I2C-address.
#
# version:  1.0 (30.12.2019)

import sys
import time
import curses  # keyboard input and UI
import Adafruit_PCA9685

screen = curses.initscr()  # create new screen
curses.echo()  # do echo keyboard input
curses.cbreak()  # do not wait for user to confirm manually
screen.keypad(True)  # enable special-keys

# start values for I2C communication and PCA-module connection
pwm = 0
bus = 0
addr = 0x00
chnl = 0

class Controller:
    def __init__(self):
        """ collects information on connection and initializes I2C-link """
   
        self.getI2Cinfo()
        self.pwm = Adafruit_PCA9685.PCA9685(address = self.addr, busnum = self.bus)
        self.getPCAinfo()
        self.sendSignal()  # start loop for signal input
 
    def getI2Cinfo(self):
        """ collects I2C information from user """
        
        screen.clear()
        screen.addstr("If you want to use default I2C-values press 'y', otherwise default values are used: ")
        screen.refresh()
        answ = screen.getch()
        
        # user is supposed to type 'y' to use standard values or any other character to provide them manually
        if answ == ord('y'):  # user confirms to use default values
            self.addr = 0x40  # default I2C address
            self.bus = 1  # default I2C busnumber (for Raspberry Pi's newer than model 1)
        
        # NOTE do not use this yet, it potentially breaks the script use default I2C data instead
        elif answ != ord('y'):  # user hands over I2C information manually
            screen.addstr("Please enter the I2C-address of your PCA9685 module: ")
            screen.refresh()
            self.addr = screen.getch() # get I2C address from user input
            screen.clear()
        
            screen.addstr("Please enter the I2C-bus of your PCA9685 module: ")
            screen.refresh()
            self.bus = screen.getch()  # get I2C busnumber from user input
     
 
    def getPCAinfo(self):
        """get PCA channel from user"""
  
        screen.clear()
        screen.addstr("Please enter the PCA9685 channel you want to send a signal to: ")
        screen.refresh()

        val1 = screen.getkey()  # first character of portnumber
        val2 = screen.getkey()  # second character of portnumber
        val0 = val1 + val2

        try:
            chnl = int(val0)  # cast string into int
            if chnl < 0 or chnl > 15:  # make sure input fits to boundaries of PCA-channels
                screen.clear()
                screen.addstr("Not a valid channel. Ending program.")
                screen.refresh()
                time.sleep(2)
                self.end()
            self.chnl = chnl
        except:  # if there are any non-int characters in the string
            screen.clear()
            screen.addstr("Not a valid channel. Ending program.")  #blame the user
            screen.refresh()
            time.sleep(2)
            self.end()
 
    def sendSignal(self):
        """ takes a pwm value from the user and pushes it to the given channel """

        screen.clear()
        screen.addstr("Please enter your pwm value: ")
        screen.refresh()
        while True:
            val1 = screen.getkey()  # first character of pwm value
            if val1 == "q":  # stop script when the q key is pressed
                self.end()
                break

            val2 = screen.getkey()  # second character of pwm value
            val3 = screen.getkey()  # third character of pwm value
            val0 = val1 + val2 + val3  # create three digit string
            
            try:
                val = int(val0)
                self.pwm.set_pwm(self.chnl, 0, val)  # push signal to channel
                screen.clear()
                screen.addstr(f"Curent value is {val}. Please enter your new pwm value: ")  # ask user for new value
                screen.refresh()
            except:  # if there are any non-int characters in the string
                screen.clear()
                screen.addstr("Input is not a valid pwm value! Please enter a valid pwm value: ")
                screen.refresh()
                time.sleep(3)
     
     
    def end(self):
        """ resets terminal settings and ends script """
        
        curses.nocbreak()
        screen.keypad(0)
        curses.echo()
        curses.endwin()
        sys.exit()
    

if __name__ == "__name__":
    cotroller = Controller()
