import time
import threading

FRONT = 0
RIGHT = 1
BACK = 2


class SensorManager:
    """ controls the measured distances to the vehicle's front, right and back """

    REFRESH_INTERVAL = 0.5

    def __init__(self):
        """ initializes the sensor manager and starts the thread that refreshes the sensor data """

        self.__distance_front = 0.0
        self.__distance_right = 0.0
        self.__distance_back = 0.0

        refresh_thread = threading.Thread(target=self.refresh)
        refresh_thread.start()

    # TODO
    def refresh(self) -> None:
        """ constantly updates the measured sensor data """

        while True:
            time.sleep(self.REFRESH_INTERVAL)

    def get_distance(self, direction: int) -> float or None:
        """ gives the latest measured distance in a certain direction

            Args:
                direction (int): number that represents the direction

            Returns:
                float: latest measured distance if the direction can be interpreted
                None: if the handed direction is not one of the directions defined at th top of this file
        """

        if direction == FRONT:
            return self.__distance_front
        elif direction == RIGHT:
            return self.__distance_right
        elif direction == BACK:
            return self.__distance_back
        else:
            return None
