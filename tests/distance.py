#This script calcuates the distance between an HC-SR04 module and the nearest object.
#author: @FrederikSchittny
#version: 1.0(07.11.2019)

import RPi.GPIO as GPIO #library for GPIO control
import time
import curses  #import for keyboard input and interface

screen = curses.initscr()  #create new screen
screen.nodelay(True) #.getch() is ignored if no keyboard input is detected
curses.noecho()  #do not echo keyboard input
curses.cbreak()  #disable return-press for input
screen.keypad(True)  #enable special-keys

GPIO.setmode(GPIO.BCM) #set GPIO mode

TRIG = 23 #trigger pin of HC-SR04 module
ECHO = 24 #echo pin of HC-SR04 module

GPIO.setup(TRIG,GPIO.OUT) #the trigger pin is an output pin
GPIO.setup(ECHO,GPIO.IN)  #to catch echo signal the pin has to be an input

GPIO.output(TRIG, False) #pull down trigger pin in case the pin is still activated
screen.addstr("Waiting For Sensor To Settle")
screen.refresh() #making an output during waiting time
time.sleep(2)   #wait two seconds to make sure there are no signal fragments which could be detected
screen.clear() #clear the output area

while True: #cycle with sensordetection
 char = screen.getch()  #get keyboard input 
 
 if char == ord('q'): #press q to exit script safely
  break #ends the cycle
 #if no keyboard input is detected .getch() is ignored
 GPIO.output(TRIG, True) #activate the trigger channel of HC-SR04 module
 time.sleep(0.00001) #10μs activate 8 ultrasound bursts at 40 kHz
 GPIO.output(TRIG, False) #deactivate trigger channel
 
 while GPIO.input(ECHO)==0: #measure time in which echo signal is detected
   pulse_start = time.time()
 
 while GPIO.input(ECHO)==1: #measure the time of the echo signal
   pulse_end = time.time()
   
 pulse_duration = pulse_end - pulse_start #time it took the signal to hit the objectand return to sensor 
 distance = pulse_duration * 17150 #calculate into cm 34300[cm/s]=Distance[cm]/(Time[s]/2)
 distance = round(distance, 2) #round the result
 screen.clear() #clear screen for next output
 screen.addstr("Distance: " + str(distance) + "cm") #output the results to the console
 screen.refresh()
 #print("Distance:",distance,"cm")
 
#in order not to mess up the console all setting-changes need to be reset to default values
GPIO.cleanup()  
curses.nocbreak()
screen.keypad(0)
curses.echo()
curses.endwin()
