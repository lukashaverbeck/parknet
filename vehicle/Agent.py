import json
from Driver import Driver
from Formation import Formation
from ui.Interface import WebInterface

ATTRIBUTES_FILE = "./attributes.json"


class Agent:
    def __init__(self):
        """ initializes a specific car agent based on his attributes file """

        # read in ID, length and with from the according file
        with open(ATTRIBUTES_FILE) as attributes_file:
            data = attributes_file.read()
            attributes = json.loads(data)
            
            self.__id = attributes["id"]
            self.__length = attributes["length"]
            self.__width = attributes["width"]

        self.__formation = Formation(self)
        self.__driver = Driver(self.__length, self.__width, self.__formation)
        self.__interface = WebInterface(self)

        self.__interface.start()

    # -- getters --

    def driver(self):
        return self.__driver

    def communication(self):
        return self.__communication

    def get_id(self):
        return self.__id
