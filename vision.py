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


def lazy_sensor_update(direction, sensor):
    """ decorator function that ensures that a distance sensor is only activated in certain time intervals
        NOTE this decorator should only be used as a decorator for distance sensor data property functions

        Args:
            direction (str): direction of the distance sensor
            sensor (DistanceSensor): sensor capturing distance data

        Returns:
            function: decorator wrapper function
    """

    def wrapper(func):
        """ wrapper function containing the update function

            Args:
                func (function): property function for a specific sensor

            Returns:
                function: decorator function updating the sensor data
        """

        def update(sensor_manager):
            """ updates a sensor data point if it is being requested and has not been updated for a while

                Args:
                    sensor_manager (SensorManager): instance of a sensor manager whose distance data is being requested

                Returns:
                    float: the result of the request being produced by the corresponding property function
            """

            timestamp = time.time()
            update_data = sensor_manager.updates[direction]

            # check if the distance value should be updated
            if update_data["time"] < timestamp - sensor_manager.REFRESH_INTERVAL:
                # update the distance value and the corresponding timestamp
                update_data["value"] = sensor.distance * 100 + const.SENSOR_COMPENSATION_DISTANCE
                update_data["time"] = timestamp

            return func(sensor_manager)
        
        return update
    return wrapper


@Singleton
class SensorManager:
    """ collects information about the distance to obstacles around the vehicle """

    REFRESH_INTERVAL = 0.1  # interval in which new values are calculated
    
    # keys for sensor data dictionary
    FRONT_KEY = "front"
    RIGHT_KEY = "right"
    REAR_KEY = "rear"
    REAR_ANGLED_KEY = "rear_angled"

    # distance sensors
    SENSOR_FRONT = DistanceSensor(echo=const.EchoPin.FRONT, trigger=const.TriggerPin.FRONT)
    SENSOR_RIGHT = DistanceSensor(echo=const.EchoPin.RIGHT, trigger=const.TriggerPin.RIGHT)
    SENSOR_REAR = DistanceSensor(echo=const.EchoPin.BACK, trigger=const.TriggerPin.BACK)
    SENSOR_REAR_ANGLED = DistanceSensor(echo=const.EchoPin.BACK_ANGLED, trigger=const.TriggerPin.BACK_ANGLED)
    
    def __init__(self):
        """ initializes the sensor manager by defining a dictionary that
            keeps track of their last update timestamps and values
        """

        self.updates = {
            self.FRONT_KEY: {
                "time": 0,
                "value": 0
            },
            self.RIGHT_KEY: {
                "time": 0,
                "value": 0
            },
            self.REAR_KEY: {
                "time": 0,
                "value": 0
            },
            self.REAR_ANGLED_KEY: {
                "time": 0,
                "value": 0
            }
        }

    @property
    @lazy_sensor_update(FRONT_KEY, SENSOR_FRONT)
    def front(self):
        """ determines the distance value of the front sensor
            NOTE this method can be used as a `property`
            NOTE this property is being updated automatically (see `lazy_sensor_update`)

            Returns:
                float: latest measured distance value
        """

        return self.updates[self.FRONT_KEY]["value"]

    @property
    @lazy_sensor_update(RIGHT_KEY, SENSOR_RIGHT)
    def right(self):
        """ determines the distance value of the right sensor
            NOTE this method can be used as a `property`
            NOTE this property is being updated automatically (see `lazy_sensor_update`)

            Returns:
                float: latest measured distance value
        """

        return self.updates[self.RIGHT_KEY]["value"]

    @property
    @lazy_sensor_update(REAR_KEY, SENSOR_REAR)
    def rear(self):
        """ determines the distance value of the rear sensor
            NOTE this method can be used as a `property`
            NOTE this property is being updated automatically (see `lazy_sensor_update`)

            Returns:
                float: latest measured distance value
        """

        return self.updates[self.REAR_KEY]["value"]

    @property
    @lazy_sensor_update(REAR_ANGLED_KEY, SENSOR_REAR_ANGLED)
    def rear_angled(self):
        """ determines the distance value of the rear angled sensor
            NOTE this method can be used as a `property`
            NOTE this property is being updated automatically (see `lazy_sensor_update`)

            Returns:
                float: latest measured distance value
        """

        return self.updates[self.REAR_ANGLED_KEY]["value"]


@Singleton
class Camera:
    """ captures images
        NOTE this class should be used as a context manager
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
                    # capture an image and save it locally
                    camera.capture(frame, "rgb")
                    self.image = frame.array


@Singleton
class FrontAgentScanner:
    """ analyzes the camera input and extracts agent IDs by scanning QR Codes """

    UPDATE_INTERVAL = 1

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
