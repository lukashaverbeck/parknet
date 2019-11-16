# test for opening up a new accesspoint.

import time
import threading
from PyAccessPoint import pyaccesspoint


access_point = pyaccesspoint.AccessPoint(ip="192.168.2.116")
thread = threading.Thread(target=access_point.start)

access_point.stop()
thread.start()
time.sleep(30)
access_point.stop()
