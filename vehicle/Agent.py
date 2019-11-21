import json
from .Driver import Driver
from .Formation import Formation
from .Communication import Communication

ATTRIBUTES_FILE = "./attributes.json"


class Agent:
    def __init__(self):
        """ initializes a specific car agent based on his attributes file """

        with open(ATTRIBUTES_FILE) as attributes_file:
            data = attributes_file.read()
            attributes = json.loads(data)
            
            self.__id = attributes["id"]
            self.__length = attributes["length"]
            self.__width = attributes["width"]

        self.__communication = Communication()
        self.__formation = Formation()
        self.__driver = Driver(self.__length, self.__width, self.__formation)

    def driver(self):
        return self.__driver

    def communication(self):
        return self.__communication