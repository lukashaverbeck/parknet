from wifi import Cell

list = Cell.all("wlan0")
for wlanscan in list:
    print(str(wlanscan.ssid) + " Quality: " + str(wlanscan.quality) + " Protected: " + str(wlanscan.encrypted))