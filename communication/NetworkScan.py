import socket as socketlib
from contextlib import closing

class NetworkScan:

    def getLocalIP(unused):
        IP1 = socketlib.gethostbyname(socketlib.gethostname())
        return IP1



    def check_if_up(ip_address):
        socket = socketlib.socket(socketlib.AF_INET, socketlib.SOCK_STREAM)
        socket.settimeout(0.004)
        try:
            with closing(socket):
                socket.connect((str(ip_address), 80))
                return True
        except socketlib.error:
            return False


    def scanIPsFromNetwork(unused):
        list = []
        IP1 = NetworkScan.getLocalIP("t")
        IPsplit = IP1.split(".")
        IPNetwork = IPsplit[0] + "." + IPsplit[1] + "." + IPsplit[2] + "."
        for i in range(1, 158):
            ip = IPNetwork + str(i)
            result = NetworkScan.check_if_up(ip)
            if result:
                #print (str(result) + ip)
                list.append(ip)
        if list.__contains__(IP1):
            list.remove(IP1)
        return list

    #print(scanIPsFromNetwork("j"))