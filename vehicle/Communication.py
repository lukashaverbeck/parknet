# allows to transfer data between different agents within a network
#
# TODO remove unnecessary GET handling
# TODO clean Serv.do_POST -> unnecessary wfile writing ?

import json
import socket as socketlib
import requests
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from contextlib import closing


def get_local_ip():
    """ determines the local IP of the current device

        Returns:
            str: local IP of the current device
    """

    ip = socketlib.gethostbyname(socketlib.gethostname())
    return ip

def check_if_up(ip_address):
    """ determines if there is a webserver is running on a given ip adress
        
        Args:
            ip_address (str): ip4 adress from the local network

        Returns:
            bool: Boolean whether the server is running (True) or not (False)
    """

    socket = socketlib.socket(socketlib.AF_INET, socketlib.SOCK_STREAM)
    socket.settimeout(0.004)
    
    try:
        with closing(socket):
            socket.connect((str(ip_address), 80))
            return True
    except socketlib.error:
        return False

def scan_ips_from_network():
    """ determines the used ip addresses in the network

        Returns:
            list: list of used ips in the network
    """

    ips = []
    local_ip = get_local_ip()
    ip_parts = local_ip.split(".")
    ip_network = ip_parts[0] + "." + ip_parts[1] + "." + ip_parts[2] + "."

    for i in range(1, 158):
        ip = ip_network + str(i)
        result = check_if_up(ip)
        if result:
            ips.append(ip)

    if local_ip in ips:
        ips.remove(local_ip)
    
    return ips


class Communication:
    """ handles the communication between multiple agents by assigning callback 
        functions to certain events 
    """

    def __init__(self, agent_id):
        """ initializes the communication component by starting a local webserver

            Args:
                agent_id (str): ID of the agent sending and receiving messages
        """

        Serv.communication = self
        self.__server = HTTPServer((get_local_ip(), 80), Serv)
        self.__callbacks = []
        self.__agent_id = agent_id

        # start server in a separate thread
        server_thread = threading.Thread(target=self.__server.serve_forever)
        server_thread.start()

    def trigger_event(self, message):
        """ triggers all events with the given topic by calling the according callback function

            Args:
                message (str): JSON serialized string of the transferred message object
        """

        # create Message object from its JSON representation
        data = json.loads(message)
        message = Message.loads(message)

        # call callback functions for the event
        for callback in self.__callbacks:
            if callback["topic"] == data["topic"]:
                callback["function"](message)

    def subscribe(self, topic, callback):
        """ subscribes to a topic by defining a callback function that is triggered when the event occours

            Args:
                topic (str): topic of the event
                callback (function): the method to run when the event occours
        """

        self.__callbacks.append({"function": callback, "topic": topic})

    def send(self, topic, content, receiver=None):
        """ sends a message with a topic to all agents in the network

            Args:
                topic (str): topic of the message
                content (object): JSON compatible object to be transferred within the network
                receiver (str or None): specifies a agent for the message to be processed by only
        """

        message = Message(self.__agent_id, topic, content, receiver)
        data = message.json_data()

        rt = requests.post("http://" + get_local_ip(), data=data)  # only for test purposes

        # send message to every agent in the network
        ips = scan_ips_from_network()
        for ip in ips:
            requests.post("http://" + ip, data=data)


class Message:
    """ helper class wrapping a transferrable message """

    def __init__(self, sender, topic, content, receiver=None):
        """ initializes a message

            Args:
                sender (str): ID of the agent sending the message
                topic (str): name of the message type
                content (object): JSON serializable object that is actually delivered through the message
                receiver (str or None): specifies a agent for the message to be processed by only
        """

        self.__sender = sender
        self.__topic = topic
        self.__content = content
        self.__receiver = receiver

    @staticmethod
    def loads(json_message):
        """ created message object from JSON serialzed message

            Args:
                json_message (str): JSON representation of a message

            Returns:
                Message: message object
        """

        message = json.loads(json_message)
        data = message["data"]
        return Message(data["sender"], message["topic"], data["content"], data["receiver"])

    def json_data(self):
        """ created a JSON serialized string of the wrapped data
            
            Returns:
                str: JSON string representing the message data
        """

        data = {
            "topic": self.__topic,
            "data": {
                "sender": self.__sender,
                "content": self.__content,
                "receiver": self.__receiver
            }
        }

        return json.dumps(data)

    # -- getters --

    def sender(self):
        return self.__sender

    def topic(self):
        return self.__topic

    def content(self):
        return self.__content

    def receiver(self):
        return self.__receiver

class Serv(BaseHTTPRequestHandler):
    """ custom http server handling POST or GET requests """ 
    
    communication = None

    def do_GET(self):
        """ handles GET request """

        if self.path == "/favicon.ico":
            self.send_response(404)
            self.end_headers()
        else:
            file_to_open = "<h1>GET</h1>"
            self.send_response(200)
            self.end_headers()
            self.wfile.write(bytes(file_to_open, "utf-8"))

    def do_POST(self):
        """ handles POST requests by triggering a communication event with the handed data """

        content_length = int(self.headers["Content-Length"])
        body = self.rfile.read(content_length)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(bytes("<h1>POST</h1>", "utf-8"))
        
        response = bytes(body).decode("utf-8")
        response_data = response.split("=" , 1)
        print("Content: " + str(response_data))

        if self.communication:
            for data in response_data:
                self.communication.trigger_event(data)
