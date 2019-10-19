from .Formation import Formation
import json

ATTRIBUTES_FILE = "./attributes.json"


class Agent:
    def __init__(self):
        """ initializes a specific car agent based on his attributes file """
        
        self.__communication = None  # TODO
        self.__driver = None         # TODO
        self.__formation = None      # TODO

        with open(ATTRIBUTES_FILE) as attributes_file:
            data = attributes_file.read()
            attributes = json.loads(data)
            
            self.__id = attributes['id']
            self.__length = attributes['length']
            self.__width = attributes['width']

    def listen_for_message(self, message) -> None:
        pass  # TODO
