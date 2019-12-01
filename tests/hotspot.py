#Opens up a standalone Wifi network with user determined network information
#version:  1.0(23.11.2019)

import time
import threading
import time
import logging
from PyAccessPoint import pyaccesspoint  #PyAccesPoint library


logging.basicConfig(format="%(asctime)s ::%(levelname)s:: %(message)s",
                        level=logging.DEBUG)

access_point = pyaccesspoint.AccessPoint(ssid="Test123" , password="Hallo123")  #create AccessPoint-object with determined ip
access_point.start()  #start a thread on running network

print (access_point.is_running());

print("Creating access point at port: 22 with IP-address: 192.168.1.001 and passwort: 1234567890")
print("In order to connect to your picar via SSH use network information and standard user information for login.")


time.sleep(30)
print("3")
time.sleep(1)
print("2")
time.sleep(1)
print("1")
time.sleep(1)

print ("Shutting down!")
access_point.stop()  #stop potential legacy acces points
#thread.start()  #start thread
access_point.stop()
