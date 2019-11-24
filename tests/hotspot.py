#Opens up a standalone Wifi network with user determined network information
#author:  @LukasGra
#author:  @lukashaverbeck
#author:  @LunaNordin
#version:  1.0(23.11.2019)

import time
import threading
from PyAccessPoint import pyaccesspoint  #PyAccesPoint library


access_point = pyaccesspoint.AccessPoint(ip="192.168.1.001")  #create AccessPoint-object with determined ip
thread = threading.Thread(target=access_point.start)  #start a thread on running network

print("Creating access point at port: 22 with IP-address: 192.168.1.001 and passwort: 1234567890")
print("In order to connect to your picar via SSH use network information and standard user information for login.")

access_point.stop()  #stop potential legacy acces points
thread.start()  #start thread
access_point.stop()
