import cv2
import time
import pyzbar.pyzbar as pyzbar

class FrontAgentScanner:
    def __init__(self):
        """ initializes the scanner and starts to refresh the front agent ID """
        self.__front_agent_id = None
        # TODO Pi-Kamera initialisieren statt Webkamera
        self.__camera = cv2.VideoCapture(0)

        refresh_frequency = 3

        while True:
            self.refresh()
            time.sleep(refresh_frequency)

    def refresh(self):
        """ updates the front agent ID based on the current video input """
        _, frame = self.__camera.read()
        decoded_objects = pyzbar.decode(frame)

        if len(decoded_objects) > 0:
            self.__front_agent_id = decoded_objects[0].data
        else:
            self.__front_agent_id = None

    def get_front_agent_id(self):
        return self.__front_agent_id;