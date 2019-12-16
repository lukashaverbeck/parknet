from projektkurs.communication import Webserver
from projektkurs.communication.Communication import Communication

""" Testing class for communication
"""



def othermethod(x):
    print("method2 "+str(x))

def testhere(x):
    print("arg was "+str(x))
    Webserver.com.send("topic2", "t2")

Webserver.com.subscribe("t", testhere)
Webserver.com.subscribe("topic2", othermethod)

Webserver.com.send("t" , "t2")