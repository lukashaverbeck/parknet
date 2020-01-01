# controlls the driving behaviour of the picar
#
# TODO implement enter_parking_lot()
# TODO implement leave_parking_lot()
# TODO test driving methods
#
# author: 	@lukashaverbeck
# author:	@LunaNordin
# version: 	3.0(1.1.2020)

import os
import csv
import logging
import time
import math
import curses
import threading
import Adafruit_PCA9685
import RPi.GPIO as GPIO
import constants as const
from datetime import datetime
from SensorManager import SensorManager
from ActionManager import ActionManager
from Camera import Camera, save_img_array
from SteeringNet import SteeringNet


class Driver:
    """ controls the steering of the vehicle """

    def __init__(self, agent, formation):
        """ initializes the driver component of an agent

            Args:
                agent (Agent): agent controlling the driver
                formation (Formation): formation of vehicles in parking lot
        """

        self.__drive_thread = None
        self.__sensor_manager = SensorManager()
        self.__action_manager = ActionManager(agent)
        self.__velocity = const.Driving.STOP_VELOCITY
        self.__angle = const.Driving.NEUTRAL_STEERING_ANGLE
        self.__length = agent.get_length()
        self.__width = agent.get_width()
        self.__mode = const.Mode.DEFAULT
        self.__mode = const.Mode.ENTER
        self.__formation = formation
        self.__recorder = None

    def start_driving(self):
        """ starts the thread that moves the vehicle """

        self.__drive_thread = self.DriveThread(self)
        self.__drive_thread.start()

    def stop_driving(self):
        """ stops and deletes the thread that moves the vehicle
            it also sets the velocity and steering angle to 0
        """

        self.set_velocity(const.Driving.STOP_VELOCITY)
        self.set_steering_angle(const.Driving.NEUTRAL_STEERING_ANGLE)

        if self.__drive_thread is not None:
            self.__drive_thread.stop()
            self.__drive_thread = None

        self.set_velocity(0.0)
        self.set_steering_angle(const.Driving.NEUTRAL_STEERING_ANGLE)

    def accelerate(self, velocity_change):
        """ changes the velocity of the vehicle
            this method does not move the vehicle but instead changes the velocity relatively

            Args:
                velocity_change (float): desired velocity change
        """

        velocity = self.__velocity + velocity_change

        if velocity > const.Driving.MAX_VELOCITY:
            velocity = const.Driving.MAX_VELOCITY
        if velocity < const.Driving.MIN_VELOCITY:
            velocity = const.Driving.MIN_VELOCITY

        self.__velocity = velocity

    def steer(self, angle_change):
        """ changes the steering angle of the vehicle
            this method does not move the vehicle's steering axle but instead changes the steering
            angle relatively

            Args:
                angle_change (float): desired angle change
        """

        angle = self.__angle + angle_change

        if angle > const.Driving.MAX_STEERING_ANGLE:
            angle = const.Driving.MAX_STEERING_ANGLE
        elif angle < const.Driving.MIN_STEERING_ANGLE:
            angle = const.Driving.MIN_STEERING_ANGLE

        self.__angle = angle

    def change_mode(self, mode):
        """ updates the behaviour of the agent by assigning an additional local action to its action manager

            best practice is not to pass the desired mode directly as a string but instead
            passing it as one of the global mode constants defined at the top of this file

            if the passed mode is not one of those modes, the vehicle's mode will be changed
            to the default mode

            Args:
                mode (str): desired mode
        """

        if mode not in const.Mode.ALL:
            mode = const.Mode.DEFAULT

        self.__action_manager.add_local_action(mode)

    # TODO
    def enter_parking_lot(self):
        """ parallel parking from a provided starting position

            for the algorithm to work the method assumes that the vehicle is parallel
            to the front vehicle or obstacle with their back fronts at the same height
        """

        self.start_driving()
        self.__velocity = 7
        time.sleep(5)
        self.stop_driving()


    # TODO
    def leave_parking_lot(self):
        """ steers the vehicle out of the parking lot """

        pass

    def search_parking_lot(self):
        """ drives straight while identifying possible parking lots and evaluating whether such a parking lot would fit
            the vehicle's dimensions for parallel parking
            after identifying a parking lot, the vehicle drives further until it reaches the start of the parking lot
        """

        check_interval = 1
        velocity = const.Driving.CAUTIOUS_VELOCITY
        intervals_with_matching_space = 0
        required_lot_length = self.__length * 1.4
        required_lot_width = self.__width * 1.2

        self.set_velocity(velocity)
        self.set_steering_angle(const.Driving.NEUTRAL_STEERING_ANGLE)
        self.start_driving()

        # evaluate whether there would be enough space in terms of width and length for parallel parking
        while self.__mode == const.Mode.SEARCH:
            if self.__sensor_manager.get_distance(const.Direction.RIGHT) >= required_lot_width:
                intervals_with_matching_space += 1
                length_with_matching_space = intervals_with_matching_space * velocity * check_interval

                if length_with_matching_space >= required_lot_length:
                    break

            time.sleep(check_interval)

        # drive further until the vehicle reaches the start of the parking lot
        while self.__sensor_manager.get_distance(const.Direction.RIGHT) >= required_lot_width:
            time.sleep(check_interval)

        self.set_velocity(const.Driving.STOP_VELOCITY)
        self.stop_driving()

    def follow_road(self):
        """ drives autonomously without explicit instructions
            by feeding the camera input through a convolutional neural network
            that predicts a steering angle and a velocity for the vehicle

            TODO add validation if a predicted angle is reasonable
        """

        steering_net = SteeringNet()
        camera = Camera.instance()

        self.set_velocity(const.Driving.CAUTIOUS_VELOCITY)
        self.set_steering_angle(const.Driving.NEUTRAL_STEERING_ANGLE)
        self.start_driving()

        while self.__mode == const.Mode.AUTONOMOUS:
            current_image = camera.get_image()
            current_angle = self.__angle
            predicted_angle = steering_net.predict(current_image, current_angle)

            self.set_steering_angle(predicted_angle)

    def move_up(self):
        """ drives as close to the front vehicle or obstacle as
            possible for the current vehicle formation
        """

        self.set_velocity(const.Driving.CAUTIOUS_VELOCITY)
        self.set_steering_angle(const.Driving.NEUTRAL_STEERING_ANGLE)

        gap = self.__formation.calc_gap()
        self.start_driving()

        while self.__sensor_manager.get_distance(const.Direction.FRONT) > gap:
            continue

        self.stop_driving()

    def move_back(self):
        """ drives as close to the front vehicle or obstacle as
            possible for the current vehicle formation
        """

        # slowly drive backwards
        self.set_velocity(-1 * const.Driving.CAUTIOUS_VELOCITY)
        self.set_steering_angle(const.Driving.NEUTRAL_STEERING_ANGLE)

        # drive as long there is enough space to the next vehicle or obstacle
        gap = self.__formation.calc_gap()
        self.start_driving()

        while self.__sensor_manager.get_distance(const.Direction.FRONT) > gap:
            time.sleep(0.5)

        self.stop_driving()

    def manual_driving(self):
        """ starts the driving thread and relies on user interfaces to change the steering data """

        self.start_driving()

    def start_recording(self):
        """ saves a continuous stream image of the current camera input and logs the corresponding
            steering angle and velocity
        """

        self.stop_recording()

        # specifies where to save the images and the log file
        data_directory = "./recorded_data/"
        log_directory = data_directory + datetime.today().strftime("%Y-%m-%d-%H-%M-%S") + "/"
        img_directory = log_directory + "img/"
        log_path = log_directory + "log.csv"

        # create the needed directories
        if not os.path.isdir(data_directory):
            os.mkdir(data_directory)

        os.mkdir(log_directory)
        os.mkdir(img_directory)

        # start recording in a separate thread
        self.__recorder = self.RecorderThread(self, log_path, img_directory)
        self.__recorder.start()

    def stop_recording(self):
        """ stops the capturing data """

        if isinstance(self.__recorder, self.RecorderThread):
            self.__recorder.stop()

        self.__recorder = None

    # -- getters --

    def get_angle(self):
        return self.__angle

    def get_velocity(self):
        return self.__velocity

    def get_sensor_manager(self):
        return self.__sensor_manager

    # -- setters --

    def set_velocity(self, velocity):
        if velocity > const.Driving.MAX_VELOCITY:
            velocity = const.Driving.MAX_VELOCITY
        elif velocity < const.Driving.MIN_VELOCITY:
            velocity = const.Driving.MIN_VELOCITY

        self.__velocity = velocity

    def set_steering_angle(self, angle):
        if angle > const.Driving.MAX_STEERING_ANGLE:
            angle = const.Driving.MAX_STEERING_ANGLE
        elif angle < const.Driving.MIN_STEERING_ANGLE:
            angle = const.Driving.MIN_STEERING_ANGLE

        self.__angle = angle

    def set_mode(self, mode):
        if mode not in const.Modes.ALL:
            mode = const.Modes.DEFAULT

        self.__mode = mode

    # -- inner classes --

    class RecorderThread(threading.Thread):
        """ thread that captures the current video input, saves it to memory
            and creates a log of the corresponding steering angle and velocity
        """

        WAIT_INTERVAL = 0.1  # seconds to wait after recording an image

        def __init__(self, driver, log_path, img_directory):
            """ initializes the thread without starting to capture the data

                Args:
                    driver (Driver): driver whose data is recorded
                    log_path (str): path to the directory of the log file
                    img_directory (str): path to the directory in which the images are saved
            """

            super().__init__()
            self.__run = True
            self.__driver = driver
            self.__camera = Camera.instance()
            self.__log_path = log_path
            self.__img_directory = img_directory
            self.__img_extension = ".jpg"

        def run(self):
            """ starts capturing the data """

            self.__camera.start()

            old_angle = self.__driver.get_angle()
            old_velocity = self.__driver.get_velocity()

            with open(self.__log_path, "a", newline="") as log:
                writer = csv.writer(log)
                writer.writerow(["image", "old_angle", "angle", "old_velocity", "velocity"])

                while self.__run:
                    img = self.__camera.get_image()
                    angle = self.__driver.get_angle()
                    velocity = self.__driver.get_velocity()

                    img_path = self.__img_directory + datetime.today().strftime("%H-%M-%S-%f") + self.__img_extension
                    save_img_array(img, img_path)
                    writer.writerow([img_path, str(old_angle), str(angle), str(old_velocity), str(velocity)])

                    old_angle = angle
                    old_velocity = velocity

                    time.sleep(self.WAIT_INTERVAL)

            return

        def stop(self):
            """ stops capturing the data """

            self.__run = False

    class DriveThread(threading.Thread):
        """ thread that moves the vehicle """

        DRIVING_INTERVAL = 1  # seconds to wait after adjusting the steering

        def __init__(self, driver):
            """ initializes the thread without starting to move the vehicle

                Args:
                    driver (Driver): driver that dictates the vehicle's steering angle and velocity
            """

            super().__init__()
            self.__driver = driver
            self.__sensor_manager = self.__driver.get_sensor_manager()
            self.__drive = True

            self.__pwm = Adafruit_PCA9685.PCA9685(address=0x40, busnum=1)  # create PCA9685-object at I2C-port
            self.__pulse_freq = 50
            self.__pwm.set_pwm_freq(self.__pulse_freq)


        def run(self):
            """ other than Driver.accelerate() or Driver.steer(), this method indeedly moves
                the vehicle according to the driver's steering angle and velocity by addressing
                the vehicle's hardware
            """

            drive_thread = threading.Thread(target=self.drive)
            steer_thread = threading.Thread(target=self.steer)

            drive_thread.start()
            steer_thread.start()

        def drive(self):
            """controlles stepper movement"""

            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(20, GPIO.OUT)
            GPIO.setup(21, GPIO.OUT)
            GPIO.setup(26, GPIO.OUT)
            self.change_stepper_status(True)

            while self.__drive:
                velocity = self.__driver.get_velocity()
                delay = self.calculate_delay(velocity)

                if velocity > 0:
                    GPIO.output(20, 0)
                else:
                    GPIO.output(20, 1)

                # ensures that there is enough space in front of or behind the vehicle by skipping the current
                # driving loop if the minimal front distance is assumed to be exceeded
                front_distance = self.__sensor_manager.get_distance(const.Direction.FRONT)
                rear_distance = self.__sensor_manager.get_distance(const.Direction.BACK)
                distance = front_distance if velocity > 0 else rear_distance
                predicted_distance = distance - abs(velocity) * self.DRIVING_INTERVAL
                if predicted_distance < const.Driving.SAFETY_DISTANCE: continue

                GPIO.output(21, GPIO.HIGH)
                time.sleep(delay)
                GPIO.output(21, GPIO.LOW)
                time.sleep(delay)


        def steer(self):
            """calculates and sets steering angle"""

            while self.__drive:
                angle = self.__driver.get_angle()
                steering_pwm_calc = self.angle_to_pmw(angle)

                start_time = time.time()
                self.__pwm.set_pwm(0, 0, steering_pwm_calc)
                print(time.time() - start_time)


        def change_stepper_status(self, status):
            """activates and deactivates controller in order to save energy"""

            if status:
                GPIO.output(26, GPIO.HIGH)
            else:
                GPIO.output(26, GPIO.LOW)



        def calculate_delay(self, velocity):
            """calculates delay time used between steps according to velocity"""

            rps = velocity / 1.729
            delay = (1 / (200 * float(rps))) / 2
            return delay


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
            """ stops the movement of the vehicle"""

            self.__drive = False
            self.change_stepper_status(False)
            self.__pwm.set_pwm(0, 0, self.angle_to_pmw(const.Driving.NEUTRAL_STEERING_ANGLE))
