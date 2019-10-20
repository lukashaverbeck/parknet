import os
import csv
import cv2
import time
import threading
from datetime import datetime


MODE_ENTER = "parking/enter"
MODE_LEAVE = "parking/leave"
MODE_SEARCH = "parking/search"
MODE_STANDBY = "parking/standby"
MODE_AUTONOMOUS = "drive/follow-road"
MODE_MANUAL = "drive/manual"
MODE_MOVE_UP = "react/move-up"
MODE_MOVE_BACK = "react/move-back"

MODE_DEFAULT = MODE_STANDBY
MODES = [MODE_ENTER, MODE_LEAVE, MODE_SEARCH, MODE_STANDBY, MODE_AUTONOMOUS, MODE_MANUAL, MODE_MOVE_UP, MODE_MOVE_BACK]


class Driver:
    """ controls the steering of the vehicle """

    def __init__(self, length, formation, mode=None):
        """ initializes the driver component of an agent

            Args:
                length (float): length of vehicle
                formation (Formation): formation of vehicles in parking lot
        """

        self.__sensor_manager = None  # TODO
        self.__velocity = 0.0
        self.__angle = 0.0
        self.__mode = mode
        self.__length = length
        self.__formation = formation
        self.__recorder = None

    # TODO
    def accelerate(self, velocity) -> None:
        """ changes the velocity of the vehicle

        Args:
            velocity (float): desired absolute velocity
        """

        pass

    # TODO
    def steer(self, angle) -> None:
        """ changes the steering angle of the vehicle

        Args:
            angle (float): desired absolute steering angle
        """

        pass

    def change_mode(self, mode) -> None:
        """ updates the behaviour of the agent by changing its mode

            best practice is not to pass the desired mode directly as a string but instead
            passing it as one of the global mode constants defined at the top of this file

            if the passed mode is not one of those modes, the vehicle's mode will be changed
            to the default mode

        Args:
            mode (str): desired mode which
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

    # TODO
    def search_parking_lot(self) -> None:
        """ drives straight while identifying possible parking lots and evaluating
            whether such a parking lot would fit the vehicle's dimensions
            the evaluation is based on sensor data
        """

        pass

    # TODO
    def follow_road(self) -> None:
        """ drives autonomously without explicit instructions
            by feeding the camera input through a convolutional neural network
            that predicts a steering angle and a velocity for the vehicle
        """

        pass

    # TODO
    def move_up(self) -> None:
        """ drives as close to the front vehicle or obstacle as
            possible for the current vehicle formation
        """

        pass

    # TODO
    def move_back(self) -> None:
        """ drives as close to the rear vehicle or obstacle as
            possible for the current vehicle formation
        """

        pass

    # TODO
    def manual_driving(self) -> None:
        """ steers the vehicle based on user inputs """

        pass

    # TODO
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

    # TODO
    def stop_recording(self) -> None:
        """ stops the recording of the camera input and the corresponding log """

        if isinstance(self.__recorder, self.RecorderThread):
            self.__recorder.stop()

        self.__recorder = None

    def get_angle(self) -> float:
        return self.__angle

    def get_velocity(self) -> float:
        return self.__velocity

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
                writer.writerow(["image", "angle", "velocity"])

            while self.__run:
                img_name = datetime.today().strftime("%H-%M-%S-%f") + ".jpg"
                angle = self.__driver.get_angle()
                velocity = self.__driver.get_velocity()

                _, frame = self.__camera.read()
                cv2.imwrite(self.__img_directory + img_name, frame)

                with open(self.__log_path, "a", newline="") as log:
                    writer = csv.writer(log)
                    writer.writerow([img_name, str(angle), str(velocity)])

                time.sleep(self.__interval)

        def stop(self) -> None:
            """ stops capturing the data """

            cv2.destroyAllWindows()
            self.__camera.release()
            self.__run = False
