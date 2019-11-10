#Script opens up a new accesspoint.

#author:	@LukasGra
#author:	@LunaNordin
#version:	0.1(09.11.2019)

from PyAccessPoint import pyaccesspoint	#library basis to create an accesspoint
import time

access_point = pyaccesspoint.AccessPoint()	#crate an accespoint-object

access_point.start()	#open up the accesspoint

while True:
	time.sleep(5)
	if access_point.is_running() == True:	#check for accespoint still being active
  		print("WLAN ist an")	
	elif access_point.is_running == False:
		print("WLAN ist aus")


##access_point.stop()

#AccessPoint:
#  def __init__(self, wlan='wlan0', inet=None, ip='192.168.45.1', netmask='255.255.255.0', ssid='MyAccessPoint', password='1234567890'):
