import requests

from projektkurs.communication.NetworkScan import NetworkScan


methods = []
args = ["unset"]


class Communication:
    def triggerEvent(topic, message):
        """ This method triggers all events with the given topic and deliver the message to them

            Args:
                topic (String): topic for the event
                message (String): message for the topic
        """

        print ("Executing")
        for item in methods:
            print("Sending Message: " + message + " Topic: " + item["topic"])
            if item["topic"] == topic:
                item['callback'](message)
    def subscribe(topic, callback):
        """ This method allows to subscribe a method to a topic

            Args:
                topic (String): topic for the event
                callback (Method): the method to run, when the event is triggered
        """
        methods.append({'callback': callback, 'topic': topic})
    def send(topic , message):
        """ This method sends a message under the given topic

            Args:
                topic (String): topic for the message
                message (String): message to be delivered
        """
        print (topic)
        """rt = requests.post("http://192.168.178.156", data={topic: message})
        """
        list = NetworkScan.scanIPsFromNetwork("e")
        for i in list:
            print(i)
            r = requests.post("http://" + i, data={topic: message})


