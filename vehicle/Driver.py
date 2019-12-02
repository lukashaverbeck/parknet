# controlls the driving behaviour of the picar
#
# TODO implement enter_parking_lot()
# TODO implement leave_parking_lot()
# TODO implement follow_road()
# TODO implement manual_driving()
# TODO implement DriveThread.velocity_to_pwm()

# author: 	@lukashaverbeck
# author:	@LunaNordin
# version: 	2.0(02.12.2019)

import os
import csv
import time
import math
import curses
import threading
import Adafruit_PCA9685
import vehicle.SensorManager as sm
from datetime import datetime
from picamera import PiCamera


MODE_ENTER = "parking/enter"
MODE_LEAVE = "parking/leave"
MODE_SEARCH = "parking/search"
MODE_STANDBY = "parking/standby"
MODE_AUTONOMOUS = "drive/follow-road"
MODE_MANUAL = "drive/manual"
MODE_MOVE_UP = "react/move-up"
MODE_MOVE_BACK = "react/move-back"

MODE_DEFAULT = MODE_MANUAL
MODES = [MODE_ENTER, MODE_LEAVE, MODE_SEARCH, MODE_STANDBY, MODE_AUTONOMOUS, MODE_MANUAL, MODE_MOVE_UP, MODE_MOVE_BACK]

CAUTIOUS_VELOCITY = 0.3  # m/s
MIN_VELOCITY = 345  # pwm
MAX_VELOCITY = 355  # pwm

MIN_STEERING_ANGLE = -35
MAX_STEERING_ANGLE = 35
NEUTRAL_STEERING_ANGLE = 0


class Driver:
    """ controls the steering of the vehicle """

    def __init__(self, length, width, formation):
        """ initializes the driver component of an agent

            Args:
                length (float): length of vehicle
                width (float): width of vehicle
                formation (Formation): formation of vehicles in parking lot
        """

        self.__drive_thread = None
        self.__sensor_manager = sm.SensorManager()
        self.__velocity = 0.0
        self.__angle = 0.0
        self.__mode = MODE_DEFAULT
        self.__length = length
        self.__width = width
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

        if self.__drive_thread is not None:
            self.__drive_thread.stop()
            self.__drive_thread = None

        self.set_velocity(0.0)
        self.set_steering_angle(0.0)

    def accelerate(self, velocity_change):
        """ changes the velocity of the vehicle
            this method does not move the vehicle but instead changes the velocity relatively

            Args:
                velocity (float): desired velocity change
        """

        velocity = self.__velocity + velocity_change

        if velocity > MAX_VELOCITY:
            velocity = MAX_VELOCITY
        elif velocity < MIN_VELOCITY:
            velocity = MIN_VELOCITY

        self.__velocity = velocity

    def steer(self, angle_change):
        """ changes the steering angle of the vehicle
            this method does not move the vehicle's steering axle but instead changes the steering
            angle relatively

            Args:
                angle (float): desired angle change
        """

        angle = self.__angle + angle_change

        if angle > MAX_STEERING_ANGLE:
            angle = MAX_STEERING_ANGLE
        elif angle < MIN_STEERING_ANGLE:
            angle = MIN_STEERING_ANGLE

        self.__angle = angle

    def change_mode(self, mode):
        """ updates the behaviour of the agent by changing its mode

            best practice is not to pass the desired mode directly as a string but instead
            passing it as one of the global mode constants defined at the top of this file

            if the passed mode is not one of those modes, the vehicle's mode will be changed
            to the default mode

            Args:
                mode (str): desired mode
        """
	self.stop_driving()

        if mode not in MODES:
            mode = MODE_DEFAULT

        self.__mode = mode

        if mode == MODE_ENTER:
            self.enter_parking_lot()
        elif mode == MODE_LEAVE:
            self.leave_parking_lot()
        elif mode == MODE_SEARCH:
            self.search_parking_lot()
        elif mode == MODE_AUTONOMOUS:
            self.follow_road()
        elif mode == MODE_MANUAL:
            self.manual_driving()
        elif mode == MODE_MOVE_UP:
            self.move_up()
        elif mode == MODE_MOVE_UP:
            self.move_back()

    # TODO
    def enter_parking_lot(self):
        """ parallel parking from a provided starting position

            for the algorithm to work the method assumes that the vehicle is parallel
            to the front vehicle or obstacle with their back fronts at the same height
        """

        pass

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
        velocity = CAUTIOUS_VELOCITY
        intervals_with_matching_space = 0
        required_lot_length = self.__length * 1.4
        required_lot_width = self.__width * 1.2

        self.set_velocity(velocity)
        self.set_steering_angle(0.0)
        self.start_driving()

        # evaluate whether there would be enough space in terms of width and length for parallel parking
        while True:
            if self.__sensor_manager.get_distance(sm.RIGHT) >= required_lot_width:
                intervals_with_matching_space += 1
                length_with_matching_space = intervals_with_matching_space * velocity * check_interval

                if length_with_matching_space >= required_lot_length:
                    break

            time.sleep(check_interval)

        # drive further until the vehicle reaches the start of the parking lot
        while self.__sensor_manager.get_distance(sm.RIGHT) >= required_lot_width:
            time.sleep(check_interval)

    # TODO
    def follow_road(self):
        """ drives autonomously without explicit instructions
            by feeding the camera input through a convolutional neural network
            that predicts a steering angle and a velocity for the vehicle
        """

        pass

    def move_up(self):
        """ drives as close to the front vehicle or obstacle as
            possible for the current vehicle formation
        """

        self.set_velocity(CAUTIOUS_VELOCITY)
        self.set_steering_angle(0.0)

        gap = self.__formation.calc_gap()
        self.start_driving()

        while self.__sensor_manager.get_distance(sm.FRONT) > gap:
            time.sleep(0.5)

        self.stop_driving()

    def move_back(self):
        """ drives as close to the front vehicle or obstacle as
            possible for the current vehicle formation
        """

        # slowly drive backwards
        self.set_velocity(-1 * CAUTIOUS_VELOCITY)
        self.set_steering_angle(0.0)

        # drive as long there is enough space to the next vehicle or obstacle
        gap = self.__formation.calc_gap()
        self.start_driving()

        while self.__sensor_manager.get_distance(sm.FRONT) > gap:
            time.sleep(0.5)

        self.stop_driving()

    # TODO
    def manual_driving(self, velocity, angle):
        """ steers the vehicle based on user inputs """

        self.start_driving()

    def start_recording(self):
        """ saves a continuos stream image of the current camera input and logs the corresponding
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

    def get_sensor_manager(self) :
        return self.__sensor_manager

    # -- setters --

    def set_velocity(self, velocity):
        if velocity > MAX_VELOCITY:
            velocity = MAX_VELOCITY
        elif velocity < MIN_VELOCITY:
            velocity = MIN_VELOCITY

        self.__velocity = velocity

    def set_steering_angle(self, angle):
        if angle > MAX_STEERING_ANGLE:
            angle = MAX_STEERING_ANGLE
        elif angle < MIN_STEERING_ANGLE:
            angle = MIN_STEERING_ANGLE

        self.__angle = angle

    # -- inner classes --

    class RecorderThread(threading.Thread):
        """ thread that captures the current video input, saves it to memory
            and creates a log of the corresponding steering angle and velocity
        """

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
            self.__camera = PiCamera(resolution=(720,480), framerate=30)
            self.__log_path = log_path
            self.__img_directory = img_directory

        def run(self):
            """ starts capturing the data """

            # write column names to log file
            with open(self.__log_path, "a", newline="") as log:
                writer = csv.writer(log)
                writer.writerow(["image", "old_angle", "angle", "old_velocity", "velocity"])

            old_angle = self.__driver.get_angle()
            old_velocity = self.__driver.get_velocity()
            data = []

            while self.__run:
                # save 15 images to the according directory
                img_name = datetime.today().strftime("%H-%M-%S-%f")
                img_path = self.__img_directory + img_name
                img_paths = [img_path + "-" + str(i) + ".jpg" for i in range(15)]
                self.__camera.capture_sequence(img_paths)

                angle = self.__driver.get_angle()
                velocity = self.__driver.get_velocity()

                # save the captured data to a local variable
                data.append({
                    "paths": img_paths,
                    "angle": angle,
                    "velocity": velocity,
                    "old_angle": old_angle,
                    "old_velocity": old_velocity
                })

                old_angle = angle
                old_velocity = velocity

            # write numerical data to log file
            with open(self.__log_path, "a", newline="") as log:
                writer = csv.writer(log)
                
                for row in data:
                    for path in row["paths"]:
                        angle = row["angle"]
                        velocity = row["velocity"]
                        old_angle = row["old_angle"]
                        old_velocity = row["old_velocity"]
                        writer.writerow([path, str(old_angle), str(angle), str(old_velocity), str(velocity)])

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
            self.__drive = True
			
	    self.__pwm = Adafruit_PCA9685.PCA9685(address=0x40, busnum=1)  # create PCA9685-object at I2C-port
	    self.__pulse_freq = 50
	    self.__pwm.set_pwm_freq(pulse_freq)

        # TODO
        def run(self):
            """ other than Driver.accelerate() or Driver.steer(), this method indeedly moves
                the vehicle according to the driver's steering angle and velocity by addressing
                the vehicle's hardware
            """
			

            while self.__drive:
                angle = self.__driver.get_angle()
                velocity = self.__driver.get_velocity()
                time.sleep(self.DRIVING_INTERVAL)
				
                steering_pwm_calc = self.angle_to_pmw(self, angle)
                
                self.__pwm.set_pwm(1, 0, velocity)
                self.__pwm.set_pwm(0, 0, int(steering_pwm_calc))

        # TODO
        def angle_to_pmw(self, x):
            """ converts the current steering angle to a pulse width modulation value that can be processed by the 
                hardware

                Returns:
                    float: pwm value for the steering angle
            """
            
            val = 0.000002*(math.pow(x,4))+0.000002*(math.pow(x,3))+0.005766*(math.pow(x,2))-(1.81281*x)+324.149
            return val

        # TODO
        def velocity_to_pmw(self):
            """ converts the current velocity to a pulse with modulation value that can be processed by that 
                hardware

                Returns:	
                    float: pwm value for the velocity
            """

            pass

        def stop(self):
            """ stops the movement of the vehicle """

            self.__drive = False
