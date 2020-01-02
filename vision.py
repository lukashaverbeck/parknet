# This module contains entities that collect information about the agent's environment
# including sensor data about the measured distances to the vehicle's front, right and back
# and visual camera data. It also uses the camera input to provide information about other agents
# in the agent's field of view.
#
# author: @LunaNordin
# author: @lukashaverbeck
# version: 2.0 (29.12.2019)
#
# TODO improve QR code analysis

import time
import picamera
import picamera.array
import RPi.GPIO as GPIO
import constants as const
import pyzbar.pyzbar as pyzbar
from util import Singleton
from threading import Thread


@Singleton
class SensorManager:
    """ collects information about the distance to obstacles around the vehicle """

    REFRESH_INTERVAL = 0.1  # interval in which new values are calculated
    
    def __init__(self):
        """ initializes the sensor manager and starts the thread that refreshes the sensor data """

        self.front = 0.0
        self.right = 0.0
        self.rear = 0.0
        self.rear_angled = 0.0
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        # define all trigger pins as outputs and all echo pins as inputs
        # make sure all pins ar free to use to avoid data collision
        GPIO.setup(const.TriggerPin.FRONT, GPIO.OUT)
        GPIO.setup(const.TriggerPin.RIGHT, GPIO.OUT)
        GPIO.setup(const.TriggerPin.BACK, GPIO.OUT)
        GPIO.setup(const.TriggerPin.BACK_ANGLED, GPIO.OUT)
        GPIO.setup(const.EchoPin.FRONT, GPIO.IN)
        GPIO.setup(const.EchoPin.RIGHT, GPIO.IN)
        GPIO.setup(const.EchoPin.BACK, GPIO.IN)
        GPIO.setup(const.EchoPin.BACK_ANGLED, GPIO.IN)

        # pull down trigger pins in case the pin is still activated
        GPIO.output(const.TriggerPin.FRONT, False)
        GPIO.output(const.TriggerPin.RIGHT, False)
        GPIO.output(const.TriggerPin.BACK, False)
        GPIO.output(const.TriggerPin.BACK_ANGLED, False)
        time.sleep(2)  # wait two seconds to make sure there are no signal fragments which could be detected

        # start updating the distances in a separate thread
        refresh_thread = Thread(target=self.update)
        refresh_thread.start()

    def update(self):
        """ constantly updates the measured distances """

        while True:
            # calculate and save distances
            self.front = self.calc_distance(const.TriggerPin.FRONT, const.EchoPin.FRONT)
            self.right = self.calc_distance(const.TriggerPin.RIGHT, const.EchoPin.RIGHT)
            self.rear = self.calc_distance(const.TriggerPin.BACK, const.EchoPin.BACK)
            #self.rear_angled = self.calc_distance(const.TriggerPin.BACK_ANGLED, const.EchoPin.BACK_ANGLED)
            
            time.sleep(self.REFRESH_INTERVAL)

    def calc_distance(self, trig_pin, echo_pin):
        """ triggers the module at given pins and calculates the measured distance

            Args:
                trig_pin (int): ID of the pin to send a signal
                echo_pin (int): ID of the pin to receive a signal
                NOTE these arguments should be passed as the according constants -> `constants.py`

            Returns:
                float: the measured distance in cm rounded to two decimal places
        """

        GPIO.output(trig_pin, True)  # activate the trigger channel of HC-SR04 module
        time.sleep(0.00001)  # 10μs pulse activates 8 ultrasound bursts at 40 kHz
        GPIO.output(trig_pin, False)  # deactivate trigger channel

        # measure time in which echo signal is detected
        while GPIO.input(echo_pin) == 0:
            pulse_start = time.time()

        # measure the time of the echo signal
        while GPIO.input(echo_pin) == 1:
            pulse_end = time.time()

        pulse_duration = pulse_end - pulse_start  # time it took the signal to hit the objectand return to sensor
        distance = pulse_duration * 17150  # calculate into cm 34300[cm/s] = Distance[cm] / (Time[s]/2)
        return round(distance, 2)


@Singleton
class Camera:
    """ captures images
        NOTE this class should be uses as a context manager
    """

    def __init__(self):
        """ initializes the camera """

        self.image = None
        self.uses = 0

    def __enter__(self):
        """ starts the camera as a context manager """

        # check if the camera was not used before
        if self.uses <= 0:
            self.uses = 1

            # start capturing images
            recorder_thread = Thread(target=self.record)
            recorder_thread.start()
        else:
            self.uses += 1

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """ leaves the context manager """

        self.uses -= 1

    def record(self):
        """ constanly takes images as long as there is at least one instance accessing the camera """

        with picamera.PiCamera() as camera:
            camera.brightness = 60

            while self.uses > 0:
                with picamera.array.PiRGBArray(camera) as frame:
                    # capture and locally save an image
                    camera.capture(frame, "rgb")
                    self.image = frame.array


@Singleton
class FrontAgentScanner:
    """ analyzes the camera input and extracts agent IDs by scanning QR Codes """

    UPDATE_INTERVAL = 3

    def __init__(self):
        """ initializes the FrontAgentScanner """

        self.id = None
        self.uses = 0

    def __enter__(self):
        """ starts the scanner as a context manager """

        # check if the scanner was not used before
        if self.uses <= 0:
            self.uses = 1

            # start analyzing the camera input
            recorder_thread = Thread(target=self.update)
            recorder_thread.start()
        else:
            self.uses += 1

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """ leaves the context manager """

        self.uses -= 1

    def update(self):
        """ constanly updates the front agent ID based on the current video input
            as long as there is at least one instance accessing the camera

            TODO add validation whether a found QR code really represents an agent ID
            -> check for multiple QR codes and select the most plausible one
        """

        with Camera.instance() as camera:
            while self.uses > 0:
                # analyze the camera input with respect to QR Codes representing an agent ID
                if camera.image is not None:
                    decoded_objects = pyzbar.decode(camera.image)

                    # check if any QR codes have been found
                    if len(decoded_objects) > 0:
                        # decode the first QR code and set the ID accordingly
                        data_bytes = decoded_objects[0].data
                        self.id = data_bytes.decode("utf-8")
                    else:
                        self.id = None

                time.sleep(self.UPDATE_INTERVAL)
