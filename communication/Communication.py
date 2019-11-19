import requests
import NetworkScan


class Communication:
    def __init__(self):
        self.__callbacks = []

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
                topic (String): topic of the event
                callback (Method): the method to run when the event occours
        """

        self.__callbacks.append({"function": callback, "topic": topic})

    def send(self, topic, message):
        """ sends a message with a topic to all agents in the network

            Args:
                topic (String): topic of the message
                message (String): message to be transferred
        """

        # rt = requests.post("http://192.168.178.156", data={topic: message})

        ips = NetworkScan.scan_ips_from_network("e")
        for ip in ips:
            requests.post("http://" + ip, data={topic: message})
