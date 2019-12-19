# This module handles the three HC-SR04 modules connected to the Picar.
# It is responsible for returning distance values requested by other classes.

# author:	@lukashaverbeck
# author:	@LunaNordin
# version:	1.2

import time
import threading
import RPi.GPIO as GPIO	 # library for GPIO control
import constants as const


class SensorManager:
    """ controls the measured distances to the vehicle's front, right and back """
            
    REFRESH_INTERVAL = 0.1	# interval in which new values are calculated
        
    def __init__(self):
        """ initializes the sensor manager and starts the thread that refreshes the sensor data """
            
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
            
        # define all trigger pins as outputs and all echo pins as inputs
        # make shure all pins ar free to use to avaoid data collision
        GPIO.setup(const.TriggerPin.HC_SR04_FRONT, GPIO.OUT)	
        GPIO.setup(const.EchoPin.HC_SR04_FRONT, GPIO.IN)	
        GPIO.setup(const.TriggerPin.HC_SR04_RIGHT, GPIO.OUT)	
        GPIO.setup(const.EchoPin.HC_SR04_RIGHT, GPIO.IN)
        GPIO.setup(const.TriggerPin.HC_SR04_BACK, GPIO.OUT)	
        GPIO.setup(const.EchoPin.HC_SR04_BACK, GPIO.IN)	
            
        GPIO.output(const.TriggerPin.HC_SR04_FRONT, False)	 # pull down trigger pin in case the pin is still activated
        time.sleep(2)  # wait two seconds to make sure there are no signal fragments which could be detected
    
        # start values for the three distances
        self.__distance_front = 0.0
        self.__distance_right = 0.0
        self.__distance_back = 0.0
    
        # start updating the distances in a separate thread
        refresh_thread = threading.Thread(target=self.refresh)
        refresh_thread.start()
        
    def sensor_distance(self, trig_pin, echo_pin):
        """ triggers the module at given pins and calculates distance """
        
        GPIO.output(trig_pin, True)	# activate the trigger channel of HC-SR04 module
        time.sleep(0.00001)	 # 10μs pulse activates 8 ultrasound bursts at 40 kHz
        GPIO.output(trig_pin, False)	 # deactivate trigger channel
    
        # measure time in which echo signal is detected
        while GPIO.input(echo_pin) == 0:
            pulse_start = time.time()
    
        # measure the time of the echo signal
        while GPIO.input(echo_pin) == 1:
            pulse_end = time.time()
    
        pulse_duration = pulse_end - pulse_start  # time it took the signal to hit the objectand return to sensor   
        distance = pulse_duration * 17150  # calculate into cm 34300[cm/s] = Distance[cm] / (Time[s]/2)
        distance = round(distance, 2)
        return distance	 # return the calculated distance value
    
    def refresh(self):
        """ constantly updates the measured sensor data """
    
        while True:
            self.__distance_front = self.sensor_distance(const.TriggerPin.HC_SR04_FRONT, const.EchoPin.HC_SR04_FRONT)
            self.__distance_right = self.sensor_distance(const.TriggerPin.HC_SR04_RIGHT, const.EchoPin.HC_SR04_RIGHT)
            self.__distance_back = self.sensor_distance(const.TriggerPin.HC_SR04_BACK, const.EchoPin.HC_SR04_BACK)
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
        if direction == const.Direction.FRONT:
            return self.__distance_front
        elif direction == const.Direction.RIGHT:
            return self.__distance_right
        elif direction == const.Direction.BACK:
            return self.__distance_back
        else:
            return None
