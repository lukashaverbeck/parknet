import socket as socketlib
from contextlib import closing

def get_local_ip(self):
    """ determines the local IP of the current device

        Returns:
            str: local IP of the current device
    """

    ip = socketlib.gethostbyname(socketlib.gethostname())
    return ip

def check_if_up(self, ip_address):
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

def scan_ips_from_network(self):
    """ determines the used ip addresses in the network

        Returns:
            list: list of used ips in the network
    """

    ips = []
    local_ip = get_local_ip("t")
    ip_parts = local_ip.split(".")
    ip_network = ip_parts[0] + "." + ip_parts[1] + "." + ip_parts[2] + "."

    for i in range(1, 158):
        ip = ip_network + str(i)
        result = check_if_up(ip)
        if result:
            ips.append(ip)

    if local_ip in ips:
        ips.remove(local_ip)
    
    return ips
