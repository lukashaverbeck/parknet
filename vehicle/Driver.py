import sys
import os.path
parent_path = os.path.abspath(os.path.join("."))
sys.path.append(parent_path)

import os
import csv
import cv2
import time
import curses
import threading
import Adafruit_PCA9685
import vehicle.SensorManager as sm
from datetime import datetime


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

MIN_STEERING_ANGLE = 270
MAX_STEERING_ANGLE = 380
NEUTRAL_STEERING_ANGLE = 310


class Driver:
    """ controls the steering of the vehicle """

    def __init__(self, length: float, width: float, formation: object):
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

        self.accelerate(0.0)
        self.steer(0.0)

    def accelerate(self, velocity: float) -> None:
        """ changes the velocity of the vehicle

            this method does not move the vehicle but instead works as a setter for the velocity

            Args:
                velocity (float): desired absolute velocity
        """

        if velocity > MAX_VELOCITY:
            velocity = MAX_VELOCITY
        elif velocity < MIN_VELOCITY:
            velocity = MIN_VELOCITY

        self.__velocity = velocity

    def steer(self, angle: float) -> None:
        """ changes the steering angle of the vehicle

            this method does not move the vehicle's steering axle but instead works as a setter
            for the steering angle

            Args:
                angle (float): desired absolute steering angle
        """

        if angle > MAX_STEERING_ANGLE:
            angle = MAX_STEERING_ANGLE
        elif angle < MIN_STEERING_ANGLE:
            angle = MIN_STEERING_ANGLE

        self.__angle = angle

    def change_mode(self, mode: str) -> None:
        """ updates the behaviour of the agent by changing its mode

            best practice is not to pass the desired mode directly as a string but instead
            passing it as one of the global mode constants defined at the top of this file

            if the passed mode is not one of those modes, the vehicle's mode will be changed
            to the default mode

            Args:
                mode (str): desired mode
        """

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
    def enter_parking_lot(self) -> None:
        """ parallel parking from a provided starting position

            for the algorithm to work the method assumes that the vehicle is parallel
            to the front vehicle or obstacle with their back fronts at the same height
        """

        pass

    # TODO
    def leave_parking_lot(self) -> None:
        """ steers the vehicle out of the parking lot """

        pass

    def search_parking_lot(self) -> None:
        """ drives straight while identifying possible parking lots and evaluating whether such a parking lot would fit
            the vehicle's dimensions for parallel parking
            after identifying a parking lot, the vehicle drives further until it reaches the start of the parking lot
        """

        check_interval = 1
        velocity = CAUTIOUS_VELOCITY
        intervals_with_matching_space = 0
        required_lot_length = self.__length * 1.4
        required_lot_width = self.__width * 1.2

        self.accelerate(velocity)
        self.steer(0.0)
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
    def follow_road(self) -> None:
        """ drives autonomously without explicit instructions
            by feeding the camera input through a convolutional neural network
            that predicts a steering angle and a velocity for the vehicle
        """

        pass

    def move_up(self) -> None:
        """ drives as close to the front vehicle or obstacle as
            possible for the current vehicle formation
        """

        self.accelerate(CAUTIOUS_VELOCITY)
        self.steer(0.0)

        gap = self.__formation.calc_gap()
        self.start_driving()

        while self.__sensor_manager.get_distance(sm.FRONT) > gap:
            time.sleep(0.5)

        self.stop_driving()

    def move_back(self) -> None:
        """ drives as close to the rear vehicle or obstacle as
            possible for the current vehicle formation
        """

        self.accelerate(-1 * CAUTIOUS_VELOCITY)
        self.steer(0.0)

        gap = self.__formation.calc_gap()
        self.start_driving()

        while self.__sensor_manager.get_distance(sm.FRONT) > gap:
            time.sleep(0.5)

        self.stop_driving()

    def manual_driving(self) -> None:
        """ steers the vehicle based on user inputs """
        screen = curses.initscr()
        curses.noecho()
        curses.cbreak()
        screen.keypad(True)

        pwm = Adafruit_PCA9685.PCA9685(address=0x40, busnum=1)  # create PCA9685-object at I2C-port
        pulse_freq = 50
        pwm.set_pwm_freq(pulse_freq)

        velocity = MIN_VELOCITY
        steering = NEUTRAL_STEERING_ANGLE
        pwm.set_pwm(1, 0, MIN_VELOCITY)
        pwm.set_pwm(0, 0, NEUTRAL_STEERING_ANGLE)

        try:
            while True:
                screen.refresh()
                char = screen.getch()  # get keyboard input
                screen.clear()
                screen.addstr("Velocity PWM: " + str(velocity) + "         Steering PWM: " + str(steering))
                if char == ord('q'):  # pressing q stops the script
                    pwm.set_pwm(1, 0, 340)
                    break
                elif char == ord('w'):  # pressing w increases speed
                    #screen.addstr("W pressed")
                    if velocity < MAX_VELOCITY:
                        velocity += 1
                        move = True
                elif char == ord('s'):  # pressing s decreases speed
                    #screen.addstr("S pressed")
                    if velocity > MIN_VELOCITY:
                        velocity -= 1
                        move = True
                elif char == ord('a'):  # pressing a steers left
                   #screen.addstr("A pressed")
                    if steering > MIN_STEERING_ANGLE:
                        steering -= 10
                        move = True
                elif char == ord('d'):  # pressing d steers right
                    #screen.addstr("D pressed")
                    if steering < MAX_STEERING_ANGLE:
                        steering += 10
                        move = True
                elif char == ord('e'):  # pressing e returns car to start condition
                    #screen.addstr("E pressed")
                    velocity = MIN_VELOCITY
                    steering = NEUTRAL_STEERING_ANGLE
                    move = True

                if move:  # move converts input to motor control
                    pwm.set_pwm(1, 0, velocity)
                    pwm.set_pwm(0, 0, steering)
        finally:
            curses.nocbreak()
            screen.keypad(0)
            curses.echo()
            curses.endwin()

    def start_recording(self) -> None:
        """ saves an image of the current camera input and logs the corresponding
            steering angle and velocity
        """

        self.stop_recording()

        data_directory = "./recorded_data/"
        log_directory = data_directory + datetime.today().strftime("%Y-%m-%d-%H-%M-%S") + "/"
        img_directory = log_directory + "img/"
        log_path = log_directory + "log.csv"

        if not os.path.isdir(data_directory):
            os.mkdir(data_directory)

        os.mkdir(log_directory)
        os.mkdir(img_directory)

        self.__recorder = self.RecorderThread(self, log_path, img_directory)
        self.__recorder.start()

    def stop_recording(self) -> None:
        """ stops the recording of the camera input and the corresponding log """

        if isinstance(self.__recorder, self.RecorderThread):
            self.__recorder.stop()

        self.__recorder = None

    def get_angle(self) -> float:
        return self.__angle

    def get_velocity(self) -> float:
        return self.__velocity

    def get_sensor_manager(self) -> object:
        return self.__sensor_manager

    class RecorderThread(threading.Thread):
        """ thread that captures the current video input, saves it to memory
            and creates a log of the corresponding steering angle and velocity
        """

        def __init__(self, driver: object, log_path: str, img_directory: str):
            """ initializes the thread without starting to capture the data

                Args:
                    driver (Driver): driver whose data is recorded
                    log_path (str): path to the directory of the log file
                    img_directory (str): path to the directory in which the images are saved
            """

            assert os.path.isdir(img_directory), "given image directory does not exist"
            assert isinstance(driver, Driver), "driver is not of type Driver"

            super().__init__()
            self.__run = True
            self.__driver = driver
            self.__camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            self.__log_path = log_path
            self.__img_directory = img_directory
            self.__interval = 0.2

        def run(self) -> None:
            """ starts capturing the data """

            with open(self.__log_path, "a", newline="") as log:
                writer = csv.writer(log)
                writer.writerow(["image", "old_angle", "angle", "old_velocity", "velocity"])

            old_angle = self.__driver.get_angle()
            old_velocity = self.__driver.get_velocity()

            while self.__run:
                img_name = datetime.today().strftime("%H-%M-%S-%f") + ".jpg"
                angle = self.__driver.get_angle()
                velocity = self.__driver.get_velocity()

                _, frame = self.__camera.read()
                cv2.imwrite(self.__img_directory + img_name, frame)

                with open(self.__log_path, "a", newline="") as log:
                    writer = csv.writer(log)
                    writer.writerow([img_name, str(old_angle), str(angle), str(old_velocity), str(velocity)])

                    old_angle = angle
                    old_velocity = velocity

                time.sleep(self.__interval)

        def stop(self) -> None:
            """ stops capturing the data """

            cv2.destroyAllWindows()
            self.__camera.release()
            self.__run = False

    class DriveThread(threading.Thread):
        """ thread that moves the vehicle """

        DRIVING_INTERVAL = 1

        def __init__(self, driver: object):
            """ initializes the thread without starting to move the vehicle

                Args:
                    driver (Driver): driver that dictates the vehicle's steering angle and velocity
            """

            assert callable(driver.get_angle), "driver does not provide a getter for the steering angle"
            assert callable(driver.get_velocity), "driver does not provide a getter for the steering angle"

            super().__init__()
            self.__driver = driver
            self.__drive = True

        # TODO
        def run(self) -> None:
            """ other than Driver.accelerate() or Driver.steer(), this method indeedly moves
                the vehicle accordingly to the driver's steering angle and velocity by addressing
                the vehicle's hardware
            """

            while self.__drive:
                angle = self.__driver.get_angle()
                velocity = self.__driver.get_velocity()
                time.sleep(self.DRIVING_INTERVAL)

        def stop(self):
            """ permits the thread to move the vehicle """

            self.__drive = False
