from projektkurs.vehicle.Communication import Communication
import requests


def test(hallo):
    print ("e" + str(hallo))
    #com.send("Halk" , "t" , 1)
    #rt = requests.post("http://" + "192.168.178.156", data={"e": "e"})
    #rt = requests.get("http://192.168.178.156")

com = Communication.instance(1)
com.subscribe("Hallo" , test)
com.send("Hallo", "test",1)
  # only for test purposes