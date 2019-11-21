# allows to transfer data between different agents within a network
#
# TODO remove unnecessary GET handling
# TODO clean Serv.do_POST -> unnecessary wfile writing ?

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

    def __init__(self):
        Serv.communication = self
        self.__server = HTTPServer((get_local_ip(), 80), Serv)
        self.__callbacks = []

        server_thread = threading.Thread(target=self.__server.serve_forever)
        server_thread.start()

    def trigger_event(self, topic, message):
        """ triggers all events with the given topic by calling the according callback function

            Args:
                topic (str): topic of the event
                message (str): message of the event
        """

        for callback in self.__callbacks:
            print("Sending Message: " + message + " Topic: " + callback["topic"])

            if callback["topic"] == topic:
                callback["function"](message)

    def subscribe(self, topic, callback):
        """ subscribes to a topic by defining a callback function that is triggered when the event occours

            Args:
                topic (str): topic of the event
                callback (function): the method to run when the event occours
        """

        self.__callbacks.append({"function": callback, "topic": topic})

    def send(self, topic, message):
        """ sends a message with a topic to all agents in the network

            Args:
                topic (str): topic of the message
                message (str): message to be transferred
        """

        rt = requests.post("http://" + get_local_ip(), data={topic: message})

        ips = scan_ips_from_network()
        for ip in ips:
            requests.post("http://" + ip, data={topic: message})


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
            self.communication.trigger_event(response_data[0] , response_data[1])
