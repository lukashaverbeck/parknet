# This module contains entities that are closely related to the vehicle itself.
# It defines Agents which are a general representation of an acting protagonist and
# a Driver controling the movement of the vehicle. Therefore a DriveThread applying this
# behaviour to the hardware and a RecorderThread handling the collecting of driving data
# is defined.
#
# author: @LukasGra
# author: @LunaNordin
# author: @lukashaverbeck
# version: 2.3 (4.1.2020)
#
# TODO implement Driver.leave_parking_lot
# TODO test everything

import os
import csv
import json
import time
import numpy as np
import interaction
import RPi.GPIO as GPIO
import Adafruit_PCA9685
import constants as const
from util import Singleton, threaded
from threading import Thread
from datetime import datetime
from ai import SteeringNet
from connection import AutoConnector, get_local_ip
from ui.interface import WebInterface
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
        self.distance = 0
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
        time.sleep(2)

        # drive back into gap with strong angle
        self.angle = -35
        self.velocity = -7
        self.drive_thread.driven_distance = 0
        self.distance = 50
        while self.drive_thread.driven_distance < self.distance:
            time.sleep(1)

        # drive back until close to wall
        self.angle = 8
        self.velocity = -6
        self.distance = 150
        self.drive_thread.driven_distance = 0
        while self.sensor_manager.rear > 30:
            time.sleep(1)

        # get into straight position
        self.angle = 35
        self.velocity = -7
        self.distance = 45
        self.drive_thread.driven_distance = 0
        while self.drive_thread.driven_distance < self.distance:
            time.sleep(1)

        # drive forward up to end of gap
        self.angle = -8
        self.velocity = 6
        self.drive_thread.driven_distance = 0
        while self.sensor_manager.front >= 10:
            print(self.sensor_manager.front)
            time.sleep(1)

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
            NOTE this mode has no particular destination and therfore does not terminate
            unless the driver is stopped explicitly
        """

        steering_net = SteeringNet()
        steering_net.load(const.Storage.DEFAULT_STEERING_MODEL)

        self.start_driving()

        with Camera.instance() as camera:
            while self.recorder_thread is not None:
                image = camera.image
                predicted_angle = steering_net.predict(image, self.angle)
                self.angle = predicted_angle

                time.sleep(0.25)

        self.stop_driving()

    def create_space(self, agent_id):
        """ creates space for an agent leaving the parking lot by moving up in the according direction
            until the agent has left the formation

            Args:
                agent_id (str): ID of the agent leaving the formation

            TODO ensure that an agent leaves a gap immediately after he left a parking lot
        """

        if agent_id not in self.formation: return

        # determine direction to drive in
        direction = -1 if self.formation.comes_before(self.agent, agent_id) else 1
        self.velocity = direction * const.Driving.CAUTIOUS_VELOCITY
        
        # the distance between the vehicles corrsponds to the 
        # seconds to wait after the vehicle left the parking lot
        wait_time = self.formation.distance(self.agent, agent_id)

        self.distance = 0
        self.start_driving()
        update_interval = 0.5

        # move up / back to create space until the vehicle left the parking lot
        while agent_id in self.formation:  # TODO add working condition 
            self.distance += abs(self.velocity * update_interval)
            time.sleep(update_interval)
        self.distance = 0

        # wait for vehicles that were located nearer to the leaving agent to move
        # and then close the gap
        gap = self.formation.calc_gap()
        time.sleep(wait_time)

        if direction == 1:
            self.velocity = -1 * const.Driving.CAUTIOUS_VELOCITY
        else:
            self.velocity = const.Driving.CAUTIOUS_VELOCITY

        while self.sensor_manager.front < gap:
            self.distance += abs(self.velocity * update_interval)
            time.sleep(update_interval)

        self.stop_driving()

    def move_up(self):
        """ drives as close to the front vehicle or obstacle as possible for the current vehicle formation """

        # slowly drive backwards
        self.velocity = const.Driving.MAX_VELOCITY
        self.angle = const.Driving.NEUTRAL_STEERING_ANGLE

        # drive as long there is enough space to the next vehicle or obstacle
        gap = self.formation.calc_gap()
        self.start_driving()
        while self.sensor_manager.front > gap: continue

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

        if self.recorder_thread is not None:
            self.recorder_thread.stop()
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
                img_filename = datetime.today().strftime("%H-%M-%S-%f") + "." + self.img_extension
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
    
    DISTANCE_PER_STEP = 0.00865

    def __init__(self):
        """ initializes the thread without starting to move the vehicle """

        super().__init__()

        self.active = True
        self.driver = Driver.instance()
        self.sensor_manager = SensorManager.instance()

        self.pwm = Adafruit_PCA9685.PCA9685(address=0x40, busnum=1)  # create PCA9685-object at I2C-port
        self.pulse_freq = 50
        self.pwm.set_pwm_freq(self.pulse_freq)

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(20, GPIO.OUT)
        GPIO.setup(21, GPIO.OUT)
        GPIO.setup(26, GPIO.OUT)
        self.driven_distance = 0

    def run(self):
        """ other than Driver.accelerate() or Driver.steer(), this method indeedly moves the vehicle according to the
            driver's steering angle and velocity by starting the threads that address the vehicle's hardware
        """

        self.steer()
        self.drive()

    @threaded
    def drive(self):
        self.change_stepper_status(True)

        while self.active:
            velocity = self.driver.velocity          
            if velocity < 0:
                GPIO.output(20, 1)
            elif velocity > 0:
                GPIO.output(20, 0)
            delay = self.calculate_delay(abs(velocity))

            # ensures that there is enough space in front of or behind the vehicle by skipping the current
            # driving loop if the minimal front distance is assumed to be exceeded
            front_distance = self.sensor_manager.front
            rear_distance = self.sensor_manager.rear
            distance = front_distance if velocity > 0 else rear_distance
            predicted_distance = distance - self.DISTANCE_PER_STEP
            if predicted_distance < const.Driving.SAFETY_DISTANCE: continue

            if delay > 0:
                GPIO.output(21, GPIO.HIGH)
                time.sleep(delay)
                GPIO.output(21, GPIO.LOW)
                time.sleep(delay)

            self.driven_distance += self.DISTANCE_PER_STEP

        self.change_stepper_status(False)

    def calculate_delay(self, velocity):
        """calculates delay time used between steps according to velocity"""
        if velocity > 0:
            rps = velocity / 1.729
            delay = (1 / (200 * float(rps))) / 2
            return delay
        else:
            return 0

    def change_stepper_status(self, status):
        """activates and deactivates controller in order to save energy"""

        if status:
            GPIO.output(26, GPIO.HIGH)
        else:
            GPIO.output(26, GPIO.LOW)

    @threaded
    def steer(self):
        """calculates and sets steering angle"""

        while self.active:
            angle = self.driver.angle
            steering_pwm_calc = self.angle_to_pmw(angle)
            self.pwm.set_pwm(0, 0, steering_pwm_calc)

    def angle_to_pmw(self, angle):
        """ converts the current steering angle to a pulse width modulation value that can be processed by the
            hardware

            Args:
                angle (int): angle in degrees to be converted to pwm

            Returns:
                int: pwm value for the steering angle
        """

        val = 2e-6 * angle ** 4 + 2e-6 * angle ** 3 + 0.005766 * angle ** 2 - 1.81281 * angle + 324.149
        return int(round(val, 0))

    def stop(self):
        """ stops the movement of the vehicle

            TODO implement method
        """

        self.active = False


def start_interface():
    """checks for new ip addresses of picar and starts interface-webserver on new ip"""

    last_ip = None

    while True:
        time.sleep(5)
        current_ips = get_local_ip().split()

        # check if a network address was found
        if len(current_ips) == 0:
            communication = interaction.Communication.instance()
            communication.lost_connection()
            continue
        elif len(current_ips) == 1:
            if not current_ips[0][:3] == "192":
                communication = interaction.Communication.instance()
                communication.lost_connection()
                continue
            else:
                current_ip = current_ips[0]
        else:
            if current_ips[0][:3] == "192":
                current_ip = current_ips[0]
            else:
                current_ip = current_ips[1]

        # restar webservers if the IP is new
        if not current_ip == last_ip:
            last_ip = current_ip
            print(f"Found new ip: {current_ip}")

            agent = Agent.instance()
            communication = interaction.Communication.instance()
            communication.set_local_ip(current_ip)
            driver = Driver.instance()
            sensor_manager = SensorManager.instance()
            action_manager = interaction.ActionManager.instance()

            interface = WebInterface(agent, driver, sensor_manager, action_manager)
            interface.start(current_ip)


if __name__ == "__main__":
    #AutoConnector.start_connector()
    #interface_thread = Thread(target = start_interface)
    #interface_thread.start()
    d = Driver.instance()
    d.enter_parking_lot()
