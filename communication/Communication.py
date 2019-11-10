import requests

from projektkurs.communication.NetworkScan import NetworkScan


def testhere(x):
    print("arg was "+str(x))

methods = []
args = ["unset"]


class Communication:
    def triggerEvent(topic, message):
        print ("Executing")
        for item in methods:
            print("Sending Message: " + message + " Topic: " + item["topic"])
            if item["topic"] == topic:
                item['callback'](message)
    def subscribe(topic, callback):
        methods.append({'callback': callback, 'topic': topic})
    def send(topic , message):
        print (topic)
        rt = requests.post("http://192.168.178.156", data={topic: message})
        list = NetworkScan.scanIPsFromNetwork("e")
        for i in list:
            print(i)
            r = requests.post("http://" + i, data={topic: message})

Communication.subscribe("t" ,testhere)


