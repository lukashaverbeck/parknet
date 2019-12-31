# This module contains entities that are closely related to the vehicle itself.
# It defines Agents which are a general representation of an acting protagonist and
# a Driver controling the movement of the vehicle. Therefore a DriveThread applying this
# behaviour to the hardware and a RecorderThread handling the collecting of driving data
# is defined.
#
# author: @LukasGra
# author: @LunaNordin
# author: @lukashaverbeck
# version: 2.0 (29.12.2019)
#
# TODO implement Driver.enter_parking_lot
# TODO implement Driver.leave_parking_lot
# TODO implement Driver.follow_road
# TODO finish implementation for DriveThread.run
# TODO implement DriveThread.stop
# TODO test everything

import os
import csv
import json
import time
import numpy as np
import interaction
import constants as const
from util import Singleton
from threading import Thread
from datetime import datetime
from vision import Camera, SensorManager

assert os.path.isfile(const.Storage.ATTRIBUTES), "required attributes file missing"
assert os.path.isdir(const.Storage.DATA), "required data directory missing"


@Singleton
class Agent:
    """ general representation of an acting protagonist """

    def __init__(self):
        """ initializes an agent by reading its attributes from the according file """

        try:
            # read attributes from attributes file
            with open(const.Storage.ATTRIBUTES) as attributes_file:
                # read the file and parse it to JSON data
                json_data = attributes_file.read()
                attributes = json.loads(json_data)

                # set attributes
                self.id = str(attributes["id"])
                self.length = float(attributes["length"])
                self.width = float(attributes["width"])
        except OSError:
            raise OSError("The attributes file could not be opened.")

    def __repr__(self):
        return f"Agent #{self.id} [length: {self.length}cm ; width: {self.width}]"


@Singleton
class Driver:
    """ controling the movement of the vehicle """

    def __init__(self):
        """ initializes the Driver """

        self.drive_thread = None
        self.recorder_thread = None
        self.velocity = const.Driving.STOP_VELOCITY
        self.angle = const.Driving.NEUTRAL_STEERING_ANGLE
        self.agent = Agent.instance()
        self.formation = interaction.Formation.instance()
        self.sensor_manager = SensorManager.instance()

    def start_driving(self):
        """ starts the thread that moves the vehicle """

        self.stop_driving()
        self.drive_thread = DriveThread()
        self.drive_thread.start()

    def stop_driving(self):
        """ stops and deletes the thread that moves the vehicle it also sets the velocity and steering angle to 0 """
	
        self.velocity = const.Driving.STOP_VELOCITY
        self.angle = const.Driving.NEUTRAL_STEERING_ANGLE

        if self.drive_thread is not None:
            self.drive_thread.stop()
            self.drive_thread = None

    def accelerate(self, velocity_diff):
        """ changes the velocity of the vehicle 
            NOTE this method does not move the vehicle but instead changes the internal velocity variable

            Args:
                velocity_diff (float): desired velocity change
        """

        try:
            velocity = self.velocity + velocity_diff
            
            # ensure that the velocity stays within the limits
            if velocity > const.Driving.MAX_VELOCITY:
                velocity = const.Driving.MAX_VELOCITY
            if velocity < const.Driving.MIN_VELOCITY:
                velocity = const.Driving.MIN_VELOCITY

            self.velocity = velocity
        except TypeError:
            raise TypeError("Tried to change the velocity by a non-numerical value.")

    def steer(self, angle_diff):
        """ changes the steering angle of the vehicle
            NOTE this method does not move the vehicle's steering axle 
            but instead changes the steering internal angle variable

            Args:
                angle_diff (float): desired angle change
        """

        try:
            angle = self.angle + angle_diff

            # ensure that the angle stays within the limits
            if angle > const.Driving.MAX_STEERING_ANGLE:
                angle = const.Driving.MAX_STEERING_ANGLE
            elif angle < const.Driving.MIN_STEERING_ANGLE:
                angle = const.Driving.MIN_STEERING_ANGLE

            self.angle = angle
        except TypeError:
            raise TypeError("Tried to change the steering angle by a non-numerical value.")

    def enter_parking_lot(self):
        """ parallel parking from a provided starting position

            NOTE the method assumes that the vehicle stands parallel to the 
            front vehicle or obstacle with their back fronts at the same height

            TODO test and implement function -> does not work yet
        """
	
        self.start_driving()
        time.sleep(1)
        
        self.angle = -35
        self.velocity = const.Driving.CAUTIOUS_VELOCITY
        time.sleep(2)

        self.velocity = const.Driving.STOP_VELOCITY
        self.angle = const.Driving.NEUTRAL_STEERING_ANGLE
        time.sleep(1)

        self.velocity = const.Driving.CAUTIOUS_VELOCITY
        while self.sensor_manager.back >= 35: continue

        self.stop_driving()

    def leave_parking_lot(self):
        """ steers the vehicle out of the parking lot
            
            TODO implement method
        """

        print("leave parking lot")
        time.sleep(5)

    def search_parking_lot(self):
        """ drives forward while identifying possible parking lots and evaluating whether 
            such a parking lot would fit the vehicle's dimensions for parallel parking
            NOTE after identifying a parking lot, the vehicle drives further until it reaches the start of the parking lot
        """

        check_interval = 1
        intervals_with_matching_space = 0
        required_lot_length = self.agent.length * 1.4
        required_lot_width = self.agent.width * 1.2

        self.velocity = const.Driving.CAUTIOUS_VELOCITY
        self.angle = const.Driving.NEUTRAL_STEERING_ANGLE
        self.start_driving()

        # evaluate whether there would be enough space in terms of width and length for parallel parking
        while True:
            if self.sensor_manager.right >= required_lot_width:
                intervals_with_matching_space += 1
                length_with_matching_space = intervals_with_matching_space * velocity * check_interval

                if length_with_matching_space >= required_lot_length: break

            time.sleep(check_interval)

        # drive further until the vehicle reaches the start of the parking lot
        while self.sensor_manager.right >= required_lot_width: continue
        self.stop_driving()

    def follow_road(self):
        """ drives autonomously without explicit instructions by propagating the camera 
            input through a convolutional neural network that predicts a steering angle

            TODO implement method
        """

        pass

    def move_up(self):
        """ drives as close to the front vehicle or obstacle as possible for the current vehicle formation """

        # slowly drive backwards
        self.velocity = const.Driving.CAUTIOUS_VELOCITY
        self.angle = const.Driving.NEUTRAL_STEERING_ANGLE

        # drive as long there is enough space to the next vehicle or obstacle
        gap = self.formation.calc_gap()
        self.start_driving()
        while self.sensor_manager.rear > gap: continue

        self.stop_driving()

    def move_back(self):
        """ drives as close to the rear vehicle or obstacle as possible for the current vehicle formation """

        # slowly drive backwards
        self.velocity = -1 * const.Driving.CAUTIOUS_VELOCITY
        self.angle = const.Driving.NEUTRAL_STEERING_ANGLE

        # drive as long there is enough space to the next vehicle or obstacle
        gap = self.formation.calc_gap()
        self.start_driving()
        while self.sensor_manager.rear > gap: continue

        self.stop_driving()

    def manual_driving(self):
        """ allows the user to steer manually and therefore solely 
            starts driving without specifing the concrete movement 
        """

        self.start_driving()

    def start_recording(self):
        """ starts a thread that saves a continuos stream image of the current
            camera input and logs the corresponding steering angle and velocity
        """

        self.stop_recording()
        self.recorder_thread = RecorderThread()
        self.recorder_thread.start()

    def stop_recording(self):
        """ stops the thread that captures the data """

        try:
            self.recorder_thread.stop()
        finally:
            self.recorder_thread = None


class RecorderThread(Thread):
    """ thread that captures the current video input, saves it to memory
        and creates a log of the corresponding steering angle and velocity
    """

    CAPTURE_INTERVAL = 0.25  # seconds to wait after saving a data point

    def __init__(self):
        """ initializes the thread without starting to capture the data """

        super().__init__()

        self.active = True
        self.driver = Driver.instance()
        self.camera = Camera.instance()

        # define directories and file paths
        date_str = datetime.today().strftime("%Y-%m-%d-%H-%M-%S")
        self.log_dir = f"{const.Storage.DATA}/{date_str}"
        self.img_dir = f"{self.log_dir}/img/"
        self.log_path = f"{self.log_dir}/log.csv"
        self.img_extension = "npy"

        # ensure that the necessary directories exist
        os.mkdir(self.log_dir)
        os.mkdir(self.img_dir)
        assert os.path.isdir(self.log_dir), "data directory could not be created"
        assert os.path.isdir(self.img_dir), "image directory could not be created"

    def run(self):
        """ starts capturing the data (image, angle, previous angle) """

        with Camera.instance() as camera:
            try:
                # create log file and write headers
                with open(self.log_path, "w+") as log:
                    writer = csv.writer(log)
                    writer.writerow(["image", "angle", "previous_angle"])
            except OSError:
                raise OSError("The attributes file could not be opened.")

            previous_angle = 0.0
            while self.active:
                if camera.image is None: continue  # skip loop if no image provided

                # save image
                img_filename =  datetime.today().strftime("%H-%M-%S-%f") + "." + self.img_extension
                np.save(self.img_dir + img_filename, camera.image)

                try:
                    # write data to csv file
                    with open(self.log_path, "a") as log:
                        writer = csv.writer(log)
                        angle = str(round(self.driver.angle, 3))
                        previous_angle = str(previous_angle)
                        writer.writerow([img_filename, angle, previous_angle])
                except OSError:
                    raise OSError("The attributes file could not be opened.")

                previous_angle = angle  # update previous angle for next loop
                time.sleep(self.CAPTURE_INTERVAL)

    def stop(self):
        """ stops capturing the data """
        
        self.active = False


class DriveThread(Thread):
    """ thread that moves the vehicle """

    DRIVING_INTERVAL = 0.2  # seconds to wait after adjusting the steering

    def __init__(self):
        """ initializes the thread without starting to move the vehicle """

        super().__init__()

        self.active = True
        self.driver = Driver.instance()
        self.sensor_manager = SensorManager.instance()

    def run(self):
        """ other than Driver.accelerate() or Driver.steer(), this method indeedly moves the vehicle 
            according to the driver's steering angle and velocity by addressing the vehicle's hardware

            TODO implement hardware control
        """

        while self.active:
            angle = self.driver.angle
            velocity = self.driver.velocity

            # ensures that there is enough space in front of or behind the vehicle by skipping 
            # the current driving loop if the minimal front distance is assumed to be exceeded
            distance = self.sensor_manager.front if velocity > 0 else self.sensor_manager.rear
            predicted_distance = distance - abs(velocity) * self.DRIVING_INTERVAL
            if predicted_distance < const.Driving.SAFETY_DISTANCE: continue

            print("drive with {angle}cm/s and {angle}°")

            time.sleep(self.DRIVING_INTERVAL)

    def stop(self):
        """ stops the movement of the vehicle

            TODO implement method
        """
        
        self.active = False
