import socket as socketlib
from contextlib import closing
from ipaddress import ip_network
from itertools import islice

IP1 = socketlib.gethostbyname(socketlib.gethostname())

print(IP1 + " + " + socketlib.gethostname())

def check_if_up(ip_address):
    socket = socketlib.socket(socketlib.AF_INET, socketlib.SOCK_STREAM)
    socket.settimeout(0.004)
    try:
        with closing(socket):
            socket.connect((str(ip_address), 80))
            return True
    except socketlib.error:
        return False


for i in range(1, 158):
    ip = "192.168.178." + str(i)
    result = check_if_up(ip)
    if result:
        print (str(result) + ip)