from threading import Thread,Event
from wifi import Cell
import time
import logging
from PyAccessPoint import pyaccesspoint
from wireless import Wireless



class AutoConnector(Thread):
    def __init__(self, event):
        Thread.__init__(self)
        self.stopped = event
        self.count = 0
        self.wlancount = 0
        self.hotspot_status = False
        self.wireless = Wireless()
        self.wlanname = ""
        self.access_point = pyaccesspoint.AccessPoint(ssid="Test Wlan",password="Hallo123")
        logging.basicConfig(format="%(asctime)s ::%(levelname)s:: %(message)s", level=logging.DEBUG)  # Enable Debug

        self.access_point.stop()

    def run(self):
        while not self.stopped.wait(5):
            self.wlancount = 0
            self.count = self.count + 1
            self.wlanscan()
            print("Loop Count: " + str(self.count) + " Wlans: " + str(self.wlancount))
            if self.wlancount <= 0:
                print("Starting hotspot")
                self.start_hotspot()
            else:
                if self.hotspot_status:
                    print("Hotspot disabling")
                    self.stop_hotspot()
                else:
                    print("Wlan connected: " + str(self.wireless.current()))
                    if self.wireless.current() != self.wlanname:
                        print("Connecting to " + str(self.wlanname))
                        print("Status: " + str(self.wireless.connect(self.wlanname, "Hallo1234")))
            # call a function

    def wlanscan(self):
        try:
            list = Cell.all("wlan0")
            for wlanscan in list:
                if wlanscan.ssid.startswith("parknet"):
                    self.wlancount = self.wlancount + 1
                    print(str(wlanscan.ssid) + " Quality: " + str(wlanscan.quality) + " Protected: " + str(
                        wlanscan.encrypted))
                    self.wlanname = wlanscan.ssid
        except:
            print ("Error")



    def start_hotspot(self):
        if not self.hotspot_status:
            logging.basicConfig(format="%(asctime)s ::%(levelname)s:: %(message)s",
                                level=logging.DEBUG)  # Enable Debug


            self.access_point.start()
            self.hotspot_status = True

    def stop_hotspot(self):
        if self.hotspot_status:
            logging.basicConfig(format="%(asctime)s ::%(levelname)s:: %(message)s",
                                level=logging.DEBUG)  # Enable Debug

            self.access_point.stop()
            self.hotspot_status = False


stopFlag = Event()
thread = AutoConnector(stopFlag)
thread.start()

#stopFlag.set() - to stop the timer