import json
import constants as const
from Driver import Driver
from Formation import Formation
from ui.Interface import WebInterface


class Agent:
    def __init__(self):
        """ initializes a specific car agent based on his attributes file """

        # read in ID, length and with from the according file
        with open(const.File.ATTRIBUTES) as attributes_file:
            data = attributes_file.read()
            attributes = json.loads(data)
            
            self.__id = attributes["id"]
            self.__length = attributes["length"]
            self.__width = attributes["width"]

        self.__formation = Formation(self)
        self.__driver = Driver(self, self.__formation)
        self.__interface = WebInterface(self)

        self.__interface.start()

    # -- getters --

    def driver(self):
        return self.__driver

    def get_id(self):
        return self.__id

    def get_length(self):
        return self.__length

    def get_width(self):
        return self.__width


Agent()
