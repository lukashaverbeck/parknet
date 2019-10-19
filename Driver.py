import os
import csv
import cv2
import time
import threading
from datetime import datetime


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
    def accelerate(self, velocity):
        """ changes the velocity of the vehicle

        Args:
            velocity (float): desired absolute velocity
        """

        pass

    # TODO
    def steer(self, angle):
        """ changes the steering angle of the vehicle

        Args:
            angle (float): desired absolute steering angle
        """

        pass

    def change_mode(self, mode):
        """ updates the behaviour of the agent by changing its mode

        Args:
            mode (str): desired mode
        """

        pass

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

    # TODO
    def search_parking_lot(self):
        """ drives straight while identifying possible parking lots and evaluating
            whether such a parking lot would fit the vehicle's dimensions
            the evaluation is based on sensor data
        """

        pass

    # TODO
    def follow_road(self):
        """ drives autonomously without explicit instructions
            by feeding the camera input through a convolutional neural network
            that predicts a steering angle and a velocity for the vehicle
        """

        pass

    # TODO
    def move_up(self):
        """ drives as close to the front vehicle or obstacle as
            possible for the current vehicle formation
        """

        pass

    # TODO
    def move_back(self):
        """ drives as close to the rear vehicle or obstacle as
            possible for the current vehicle formation
        """

        pass

    # TODO
    def manual_driving(self, inputs):
        """ steers the vehicle based on user inputs

            Args:
                inputs (dict): user input for the desired steering angle and velocity
        """
        pass

    # TODO
    def start_recording(self):
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
    def stop_recording(self):
        """ stops the recording of the camera input and the corresponding log """

        if isinstance(self.__recorder, self.RecorderThread):
            self.__recorder.stop()

        self.__recorder = None

    def get_angle(self):
        return self.__angle

    def get_velocity(self):
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

        def run(self):
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

        def stop(self):
            """ stops capturing the data """

            cv2.destroyAllWindows()
            self.__camera.release()
            self.__run = False
