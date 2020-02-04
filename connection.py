# This module contains entities that are closely related to creating, maintaining and
# accessing a local network of agents.
# It defines a local webserver handing POST requests that are sent between multiple agents
# and a connector that ensures that a connection between the vehicles is created.
# it also implements utility funcions that provide information about the network.
#
# version: 1.0 (1.1.2020)
#
# TODO simplify code in `AutoConnector`

import os
import time
import logging
import vehicle
import requests
import traceback
import netifaces as ni
import socket as socketlib
import constants as const
from wifi import Cell
from wireless import Wireless
from contextlib import closing
from threading import Thread, Event
from PyAccessPoint import pyaccesspoint
from http.server import BaseHTTPRequestHandler

logging.basicConfig(format="%(asctime)s ::%(levelname)s:: %(message)s", level=logging.DEBUG)


def get_local_ip():
    """ determines the local IP of the current device

        Returns:
            str: local IP of the current device
    """

    f = os.popen('hostname -I')
    ip = f.read()
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


class Server(BaseHTTPRequestHandler):
    """ custom http server handling POST or GET requests """

    communication = None

    def do_GET(self):
        """ handles GET request
        
            Raises:
                AttributeError: in case of the communication instance has not been set
        """

        if self.path == "/favicon.ico":
            self.send_response(404)
            self.end_headers()
        else:
            try:
                file_to_open = "<h1>Agent</h1> <p>ID: "+ self.communication.agent.id + "</p>"
            except AttributeError:
                raise AttributeError(
                    "The class `Server` was not provided with a communication instance before a POST request was sent.")

            self.send_response(200)
            self.end_headers()
            self.wfile.write(bytes(file_to_open, "utf-8"))

    def do_POST(self):
        """ handles POST requests by triggering a communication event """

        content_length = int(self.headers["Content-Length"])
        body = self.rfile.read(content_length)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(bytes("<h1>POST</h1>", "utf-8"))

        response = bytes(body).decode("utf-8")
        response_data = response.split("=", 1)

        try:
            # trigger event callbacks
            for data in response_data:
                self.communication.trigger(data)
        except AttributeError:
            raise AttributeError(
                "The class `Server` was not provided with a communication instance before a POST request was sent.")


class SSIDBlock:
    def __init__(self, ssid, blocktime):
        self.blocktime = blocktime
        self.ssid = ssid

    def __repr__(self):
        return f"SSIDBlock [#{self.ssid} {self.blocktime}]"


class AutoConnector(Thread):
    def __init__(self, event):
        super().__init__()

        self.stopped = event
        self.count = 0
        self.wlan_count_found = 0
        self.wireless_module = Wireless()

        self.wlan_name_found_to_connect = ""
        self.wlan_name_found_to_connect_time = 999999999999

        self.access_point = pyaccesspoint.AccessPoint(ssid="Test Wlan", password=const.Connection.WLAN_PASSWORD)
        self.access_point.stop()

        self.hotspot_status = False
        self.own_wlan_name_from_hotspot = "parknet"
        self.own_wlan_time_from_hotspot = 9999999999999

        self.last_wlan_connected = "unset"
        self.block_list = []

    def run(self):
        while not self.stopped.wait(5):
            self.wlan_count_found = 0
            self.count += 1
            print(f"Connected with: {self.wireless_module.current()}")

            if self.wireless_module.current() is None:
                if self.last_wlan_connected != "unset":
                    time_for_block = int(time.time()) + 60
                    self.add_to_block_list(self.last_wlan_connected, time_for_block)
                    self.last_wlan_connected = "unset"
            else:
                self.last_wlan_connected = self.wireless_module.current()

            self.wlan_scan()
            print(f"Loop Count: {self.count} Wlans: {self.wlan_count_found}")
            self.connect_to_network_or_create_hotspot()

    def wlan_scan(self):
        self.wlan_name_found_to_connect = ""
        self.wlan_name_found_to_connect_time = 999999999999

        try:
            wlan_scans = Cell.all("wlan0")
            for wlan_scan in wlan_scans:
                if wlan_scan.ssid.startswith("parknet"):
                    if wlan_scan.ssid != self.own_wlan_name_from_hotspot:
                        try:
                            time_wlan_create = int(wlan_scan.ssid.replace("parknet", ""))
                            if time_wlan_create < self.wlan_name_found_to_connect_time:
                                if not self.is_blocked(str(wlan_scan.ssid)):
                                    print(
                                        f"{wlan_scan.ssid} Quality: {wlan_scan.quality} Protected: {wlan_scan.encrypted}")

                                    self.wlan_count_found += 1
                                    self.wlan_name_found_to_connect = wlan_scan.ssid
                                    self.wlan_name_found_to_connect_time = time_wlan_create
                                else:
                                    print(f"Blocked Wlan Hotspot Found: {wlan_scan.ssid}")
                        except ValueError:
                            print(f"Wrong Wlan Hotspot Found: {wlan_scan.ssid.replace('parknet', '')}")
                    else:
                        print(
                            f"Found own hotspot {wlan_scan.ssid} Quality: {wlan_scan.quality} Protected: {wlan_scan.encrypted}")

                if wlan_scan.ssid == "Lukas123":
                    print("Found Lukas Wlan")

                    self.wlan_name_found_to_connect = wlan_scan.ssid
                    self.wlan_name_found_to_connect_time = 1
                    self.wlan_count_found += 1
                    break
        except:
            print(f"Error while scanning for wifi {traceback.format_exc()}")

    def start_hotspot(self):
        if not self.hotspot_status:
            print("Starting hotspot")

            self.own_wlan_name_from_hotspot = "parknet" + str(int(time.time()))
            self.own_wlan_time_from_hotspot = int(time.time())
            self.access_point.ssid = self.own_wlan_name_from_hotspot

            self.access_point.start()
            self.hotspot_status = True
            vehicle.start_interface()

    def stop_hotspot(self):
        if self.hotspot_status:
            print("Disabling hotspot")

            self.access_point.stop()
            self.hotspot_status = False
            self.own_wlan_time_from_hotspot = 9999999999999

    def connect_to_network_or_create_hotspot(self):
        if self.wlan_count_found <= 0:
            print("Hotspot mode")
            self.start_hotspot()
        elif self.own_wlan_time_from_hotspot > self.wlan_name_found_to_connect_time:
            if self.hotspot_status:
                print("Hotspot mode off")
                self.stop_hotspot()
            elif self.wireless_module.current() != self.wlan_name_found_to_connect:
                print(f"Connecting to network {self.wlan_name_found_to_connect}")
                print(
                    f"Status: {self.wireless_module.connect(self.wlan_name_found_to_connect, const.Connection.WLAN_PASSWORD)}")
                time.sleep(2)
                print(f"Wlan network: {self.wireless_module.current()}")
                vehicle.start_interface()

                if self.wireless_module.current() is not None:
                    self.last_wlan_connected = self.wireless_module.current()

    def is_blocked(self, ssid):
        for block in self.block_list:
            if block.ssid == ssid and block.blocktime > int(time.time()):
                return True
            else:
                return False

        return False

    def add_to_block_list(self, ssid, blocktime):
        self.block_list.append(SSIDBlock(ssid, blocktime))
        print(f"Blocking {ssid} for {blocktime}")

    def print_list(self):
        for block in self.block_list:
            print(f"{block} Blocked: {self.is_blocked(block.ssid)}")

    @staticmethod
    def start_connector():
        stopFlag = Event()
        thread = AutoConnector(stopFlag)
        thread.start()
