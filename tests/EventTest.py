from projektkurs.communication.Communication import Communication


def othermethod(x):
    print("method2 "+str(x))

##EventHandlerTest.registerInEvent(othermethod)

##EventHandlerTest.runEvent("Command here")

Communication.send("t" , "t2")