#This script calcuates the distance between an HC-SR04 module and the nearest object.
#It is capable of handling multiple modules simultaneously.
#author: @FrederikSchittny
#version: 2.0(07.11.2019)

import RPi.GPIO as GPIO	#library for GPIO control
import time
import curses  #import for keyboard input and interface

screen = curses.initscr()  #create new screen
screen.nodelay(True)	#.getch() is ignored if no keyboard input is detected
curses.noecho()  #do not ECHO_1 keyboard input
curses.cbreak()  #disable return-press for input
screen.keypad(True)  #enable special-keys

GPIO.setmode(GPIO.BCM)	#set GPIO mode

TRIG_1 = 23	#trigger pin of HC-SR04 module(front)
TRIG_2 = 22 #trigger pin of HC-SR04 module(side)
ECHO_1 = 24	#echo pin of HC-SR04 module(front)
ECHO_2 = 27	#echo pin of HC-SR04 module(side)

#define all trigger pins as outputs and all echo pins as inputs
GPIO.setup(TRIG_1,GPIO.OUT)	
GPIO.setup(ECHO_1,GPIO.IN)	
GPIO.setup(TRIG_2,GPIO.OUT)	
GPIO.setup(ECHO_2,GPIO.IN)	


def sensordistance (trigpin, echopin):	#function gets distance value from the module with the reported pins
  GPIO.output(trigpin, True)	#activate the trigger channel of HC-SR04 module
  time.sleep(0.00001)	#10μs activate 8 ultrasound bursts at 40 kHz
  GPIO.output(trigpin, False)	#deactivate trigger channel
  
  while GPIO.input(echopin)==0:	#measure time in which echo signal is detected
   pulse_start = time.time()
   
  while GPIO.input(echopin)==1:	#measure the time of the echo signal
   pulse_end = time.time()
   
  pulse_duration = pulse_end - pulse_start	#time it took the signal to hit the objectand return to sensor   
  distance = pulse_duration * 17150	#calculate into cm 34300[cm/s]=Distance[cm]/(Time[s]/2)
  distance = round(distance, 2)	#round the result
  return distance	#return the calculated distance value


GPIO.output(TRIG_1, False)	#pull down trigger pin in case the pin is still activated
screen.addstr("Waiting For Sensor To Settle")
screen.refresh()	#making an output during waiting time
time.sleep(2)	#wait two seconds to make sure there are no signal fragments which could be detected
screen.clear()	#clear the output area

while True:	#cycle with sensordetection
 char = screen.getch()  #get keyboard input 
 if char == ord('q'):	#press q to exit script safely
  break	#ends the cycle
 
 distance_1 = sensordistance(TRIG_1, ECHO_1)	#call sensordetection function for front module
 distance_2 = sensordistance(TRIG_2, ECHO_2)	#call sensordetection function for side module
 
 screen.clear()	#clear screen for next output
 screen.addstr("Distance_front: " + str(distance_1) + "cm			" + "Distance_side: " + str(distance_2) + "cm")	#output the results on the console
 screen.refresh()
 #print("Distance:",distance,"cm")
 
#in order not to mess up the console all setting-changes need to be reset to default values 
GPIO.cleanup()  
curses.nocbreak()
screen.keypad(0)
curses.echo()
curses.endwin()
