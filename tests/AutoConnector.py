from threading import Thread, Event
from wifi import Cell
import time
import logging
from PyAccessPoint import pyaccesspoint
from wireless import Wireless
import traceback


class ssid_block_object():
    def __init__(self, ssid, blocktime):
        self.blocktime = blocktime
        self.ssid = ssid

    def get_ssid(self):
        return self.ssid

    def get_block_time(self):
        return self.blocktime

class AutoConnector(Thread):

    def __init__(self, event):
        Thread.__init__(self)
        self.stopped = event
        self.count = 0
        self.wlan_count_found = 0
        self.hotspot_status = False
        self.wireless_module = Wireless()
        self.wlan_name_found_to_connect = ""
        self.wlan_name_found_to_connect_time = 999999999999
        self.wlan_default_password = "Hallo1234"
        self.own_wlan_name_from_hotspot = "parknet"
        self.own_wlan_time_from_hotspot = 9999999999999
        self.last_wlan_connected = "unset"
        self.block_list = []
        self.access_point = pyaccesspoint.AccessPoint(ssid="Test Wlan", password=self.wlan_default_password)
        logging.basicConfig(format="%(asctime)s ::%(levelname)s:: %(message)s", level=logging.DEBUG)  # Enable Debug

        self.access_point.stop()

    def run(self):
        while not self.stopped.wait(5):
            self.wlan_count_found = 0
            self.count = self.count + 1
            print("Connected with: " + self.wireless_module.current())
            if self.wireless_module.current() is None:
                if self.last_wlan_connected != "unset":
                    self.add_to_block_list(self.last_wlan_connected, int(time.time()) + 60)
                    self.last_wlan_connected = "unset"
            self.wlanscan()
            print("Loop Count: " + str(self.count) + " Wlans: " + str(self.wlan_count_found))
            self.connect_to_Network_or_create_hotspot()
            # call a function

    def wlanscan(self):
        self.wlan_name_found_to_connect = ""
        self.wlan_name_found_to_connect_time = 999999999999
        try:
            list = Cell.all("wlan0")
            for wlanscan in list:
                if wlanscan.ssid.startswith("parknet"):
                    if wlanscan.ssid != self.own_wlan_name_from_hotspot:
                        try:
                            time_wlan_create = int(wlanscan.ssid.replace("parknet", ""))
                            if time_wlan_create < self.wlan_name_found_to_connect_time:
                                if not self.is_blocked(wlanscan.ssid):
                                    self.wlan_count_found = self.wlan_count_found + 1
                                    print(str(wlanscan.ssid) + " Quality: " + str(wlanscan.quality) + " Protected: " + str(
                                        wlanscan.encrypted))
                                    self.wlan_name_found_to_connect = wlanscan.ssid
                                    self.wlan_name_found_to_connect_time = time_wlan_create
                                else:
                                    print("Blocked Wlan Hotspot Found:" + wlanscan.ssid)
                        except ValueError:
                            print("Wrong Wlan Hotspot Found:" + str(wlanscan.ssid.replace("parknet", "")))
                    else:
                        print("Found own hotspot " + str(wlanscan.ssid) + " Quality: " + str(
                            wlanscan.quality) + " Protected: " + str(
                            wlanscan.encrypted))
                if wlanscan.ssid == "Lukas123":
                    self.wlan_name_found_to_connect = wlanscan.ssid
                    self.wlan_name_found_to_connect_time = 1
                    print("Found Lukas Wlan!!!11")
                    break
        except:
            print("Error while scanning for wifi " + str(traceback.format_exc()))

    def start_hotspot(self):
        if not self.hotspot_status:
            logging.basicConfig(format="%(asctime)s ::%(levelname)s:: %(message)s",
                                level=logging.DEBUG)  # Enable Debug
            self.own_wlan_name_from_hotspot = "parknet" + str(int(time.time()))
            self.own_wlan_time_from_hotspot = int(time.time())
            self.access_point.ssid = self.own_wlan_name_from_hotspot

            self.access_point.start()
            self.hotspot_status = True

    def stop_hotspot(self):
        if self.hotspot_status:
            logging.basicConfig(format="%(asctime)s ::%(levelname)s:: %(message)s",
                                level=logging.DEBUG)  # Enable Debug

            self.access_point.stop()
            self.hotspot_status = False
            self.own_wlan_time_from_hotspot = 9999999999999

    def connect_to_Network_or_create_hotspot(self):
        if self.wlan_count_found <= 0:
            print("Starting hotspot...")
            self.start_hotspot()
        else:
            if self.own_wlan_time_from_hotspot > self.wlan_name_found_to_connect_time:
                if self.hotspot_status:
                    print("Disabling hotspot...")
                    self.stop_hotspot()
                else:
                    print("Wlan connected: " + str(self.wireless_module.current()))
                    if self.wireless_module.current() != self.wlan_name_found_to_connect:
                        print("Connecting to " + str(self.wlan_name_found_to_connect))
                        print("Status: " + str(
                            self.wireless_module.connect(self.wlan_name_found_to_connect, self.wlan_default_password)))

    def is_blocked(self,ssid):
        for block_obj in self.block_list:
            if block_obj.get_ssid == ssid:
                if block_obj.get_block_time() > int(time.time()):
                    return True
                else:
                    return False
        return False

    def add_to_block_list(self,ssid, blocktime):
        self.block_list.append(ssid_block_object(ssid, blocktime))
        print ("--------------------Blocking " + ssid )

    def print_list(self):
        for block_obj in self.block_list:
            print(block_obj.get_ssid() + " " + str(block_obj.get_block_time()) + " Blocked: " + str(
                self.is_blocked(block_obj.get_ssid)))


stopFlag = Event()
thread = AutoConnector(stopFlag)
thread.start()

# stopFlag.set() - to stop the timer
