from projektkurs.communication.Communication import Communication

""" Testing class for communication
"""

def othermethod(x):
    print("method2 "+str(x))

def testhere(x):
    print("arg was "+str(x))

Communication.subscribe("t", testhere)

Communication.send("t" , "t2")