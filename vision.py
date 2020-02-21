# This module contains entities that collect information about the agent's environment
# including sensor data about the measured distances to the vehicle's front, right and back
# and visual camera data. It also uses the camera input to provide information about other agents
# in the agent's field of view.
#
# version: 1.0 (29.12.2019)
#
# TODO improve QR code analysis

import time
from threading import Thread
import picamera
import picamera.array
from gpiozero import DistanceSensor
import pyzbar.pyzbar as pyzbar
import constants as const
from util import Singleton, threaded


@Singleton
class SensorManager:
    """ collects information about the distance to obstacles around the vehicle """

    REFRESH_INTERVAL = 0.1  # interval in which new values are calculated
    
    def __init__(self):
        """ initializes the sensor manager and starts the thread that refreshes the sensor data """

        self.sensor_front = DistanceSensor(echo=const.EchoPin.FRONT, trigger=const.TriggerPin.FRONT)
        self.sensor_right = DistanceSensor(echo=const.EchoPin.RIGHT, trigger=const.TriggerPin.RIGHT)
        self.sensor_back = DistanceSensor(echo=const.EchoPin.BACK, trigger=const.TriggerPin.BACK)
        self.sensor_back_angled = DistanceSensor(echo=const.EchoPin.BACK_ANGLED, trigger=const.TriggerPin.BACK_ANGLED)

        self.updates = {
            "front": {
                "time": 0,
                "value": 0
            },
            "right": {
                "time": 0,
                "value": 0
            },
            "rear": {
                "time": 0,
                "value": 0
            },
            "rear_angled": {
                "time": 0,
                "value": 0
            }
        }

        front = self.sensor_front.distance * 100
        print(front)

    @property
    def front(self):
        direction = "front"
        if self.updates[direction]["time"] < time.time()-self.REFRESH_INTERVAL:
            self.updates[direction]["value"] = self.sensor_front.distance * 100
            self.updates[direction]["time"] = time.time()
        return self.updates[direction]["value"]   

    @property
    def right(self):
        direction = "right"
        if self.updates[direction]["time"] < time.time() - self.REFRESH_INTERVAL:
            self.updates[direction]["value"] = self.sensor_right.distance * 100
            self.updates[direction]["time"] = time.time()
        return self.updates[direction]["value"]

    @property
    def rear(self):
        direction = "rear"
        if self.updates[direction]["time"] < time.time() - self.REFRESH_INTERVAL:
            self.updates[direction]["value"] = self.sensor_back.distance * 100
            self.updates[direction]["time"] = time.time()
        return self.updates[direction]["value"]

    @property
    def rear_angled(self):
        direction = "rear_angled"
        if self.updates[direction]["time"] < time.time() - self.REFRESH_INTERVAL:
            self.updates[direction]["value"] = self.sensor_back_angled.distance * 100
            self.updates[direction]["time"] = time.time()
        return self.updates[direction]["value"]


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
            self.record()
        else:
            self.uses += 1

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """ leaves the context manager """

        self.uses -= 1

    @threaded
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
            self.update()
        else:
            self.uses += 1

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """ leaves the context manager """

        self.uses -= 1

    @threaded
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
