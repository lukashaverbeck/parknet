import RPi.GPIO as GPIO
import time
import curses  #import for keyboard input

screen = curses.initscr()  #create new screen
screen.nodelay(True)
curses.noecho()  #do not echo keyboard input
curses.cbreak()  #disable return-press for input
screen.keypad(True)  #enable special-keys

GPIO.setmode(GPIO.BCM)

TRIG = 23
ECHO = 24

GPIO.setup(TRIG,GPIO.OUT)
GPIO.setup(ECHO,GPIO.IN)

GPIO.output(TRIG, False)
screen.addstr("Waiting For Sensor To Settle")
screen.refresh()
time.sleep(2)
screen.clear()

while True:
 char = screen.getch()  #get keyboard input 
 screen.clear()
 if char == ord('q'):
  break
 GPIO.output(TRIG, True)
 time.sleep(0.00001)
 GPIO.output(TRIG, False)
 
 while GPIO.input(ECHO)==0:
   pulse_start = time.time()
 
 while GPIO.input(ECHO)==1:
   pulse_end = time.time()
   
 pulse_duration = pulse_end - pulse_start   
 distance = pulse_duration * 17150
 distance = round(distance, 2)
 screen.addstr("Distance: " + str(distance) + "cm")
 screen.refresh()
 #print("Distance:",distance,"cm")
 
 
 
   
GPIO.cleanup()  
curses.nocbreak()
screen.keypad(0)
curses.echo()
curses.endwin()