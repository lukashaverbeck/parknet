# This class handles the three HC-SR04 modules connected to the Picar.
# It is responsible for returning distance values requested by other classes. 

# author:	@lukashaverbeck
# author:	@LunaNordin
# version:	0.1.1(08.11.2019)

import time
import threading

class SensorManager:
    """ controls the measured distances to the vehicle's front, right and back """
		
    REFRESH_INTERVAL = 0.5	#interval in which new values are calculated

    def __init__(self):
        """ initializes the sensor manager and starts the thread that refreshes the sensor data """

		#start values for the three distances
        self.__distance_front = 0.0
        self.__distance_right = 0.0
        self.__distance_back = 0.0

        #setup a new thread to avoid using while True: 
		refresh_thread = threading.Thread(target=self.refresh)
        refresh_thread.start()

    # TODO
    def refresh(self) -> None:
        """ constantly updates the measured sensor data """

        while True:
            time.sleep(self.REFRESH_INTERVAL)	#pause to keep timing in interval

    def get_distance(self, direction: int) -> float or None:
        """ gives the latest measured distance in a certain direction

            Args:
                direction (int): number that represents the direction

            Returns:
                float: latest measured distance if the direction can be interpreted
                None: if the handed direction is not one of the directions defined at th top of this file
        """
		#the input request is analyzed and the corresponding value is returned
        if direction == FRONT:
            return self.__distance_front
        elif direction == RIGHT:
            return self.__distance_right
        elif direction == BACK:
            return self.__distance_back
        else:
            return None
