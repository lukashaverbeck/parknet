# This module handles the three HC-SR04 modules connected to the Picar.
# It is responsible for returning distance values requested by other classes.

import time
import threading
import RPi.GPIO as GPIO	 # library for GPIO control

FRONT, RIGHT, BACK = 0, 1, 2


class SensorManager:
    """ controls the measured distances to the vehicle's front, right and back """
            
    REFRESH_INTERVAL = 0.1	# interval in which new values are calculated
        
    TRIG_1 = 23  # trigger pin of HC-SR04 module(front)
    TRIG_2 = 22  # trigger pin of HC-SR04 module(side)
    TRIG_3 = 2   # trigger pin of HC-SR04 module(back)
    ECHO_1 = 24  # echo pin of HC-SR04 module(front)
    ECHO_2 = 27  # echo pin of HC-SR04 module(side)
    ECHO_3 = 17  # echo pin of HC-SR04 module(back)

    def __init__(self):
        """ initializes the sensor manager and starts the thread that refreshes the sensor data """
            
        GPIO.setmode(GPIO.BCM)  # set GPIO mode 
        GPIO.setwarnings(False)  # do not output warnings
            
        # define all trigger pins as outputs and all echo pins as inputs
        GPIO.setup(self.TRIG_1,GPIO.OUT)	
        GPIO.setup(self.ECHO_1,GPIO.IN)	
        GPIO.setup(self.TRIG_2,GPIO.OUT)	
        GPIO.setup(self.ECHO_2,GPIO.IN)
        GPIO.setup(self.TRIG_3,GPIO.OUT)	
        GPIO.setup(self.ECHO_3,GPIO.IN)	
            
        GPIO.output(self.TRIG_1, False)	# pull down trigger pin in case the pin is still activated
        time.sleep(2)	# wait two seconds to make sure there are no signal fragments which could be detected
    
        # start values for the three distances
        self.__distance_front = 0.0
        self.__distance_right = 0.0
        self.__distance_back = 0.0
    
        # setup a new thread to avoid using "while True:" directly: 
        refresh_thread = threading.Thread(target=self.refresh)
        refresh_thread.start()
        
    def sensordistance (self, trigpin, echopin):
        """ triggers the module at given pins and calculates distance """
        
        GPIO.output(trigpin, True)	# activate the trigger channel of HC-SR04 module
        time.sleep(0.00001)	 # 10μs pulse activates 8 ultrasound bursts at 40 kHz
        GPIO.output(trigpin, False)	 # deactivate trigger channel
    
        # measure time in which echo signal is detected
        while GPIO.input(echopin)==0:
            pulse_start = time.time()
    
        # measure the time of the echo signal
        while GPIO.input(echopin)==1:
            pulse_end = time.time()
    
        pulse_duration = pulse_end - pulse_start  # time it took the signal to hit the objectand return to sensor   
        distance = pulse_duration * 17150  # calculate into cm 34300[cm/s]=Distance[cm]/(Time[s]/2)
        distance = round(distance, 2)  # round the result
        return distance	 # return the calculated distance value
    
    def refresh(self):
        """ constantly updates the measured sensor data """
    
        while True:
            self.__distance_front = self.sensordistance(self.TRIG_1, self.ECHO_1)  # call sensordetection function for front module
            self.__distance_right = self.sensordistance(self.TRIG_2, self.ECHO_2)  # call sensordetection function for side module
            self.__distance_back = self.sensordistance(self.TRIG_3, self.ECHO_3)  # call sensordetection function for back module
            time.sleep(self.REFRESH_INTERVAL)  # pause to keep timing in interval
    
    def get_distance(self, direction):
        """ gives the latest measured distance in a certain direction
            
            Args:
                direction (int): integer representing the direction of the measured distance (0 - 2)

            Returns:
                float: measured distance
                None: if an unknown direction was provided
        """
    
        # the input request is analyzed and the corresponding value is returned
        if direction == FRONT:
            return self.__distance_front
        elif direction == RIGHT:
            return self.__distance_right
        elif direction == BACK:
            return self.__distance_back
        else:
            return None
