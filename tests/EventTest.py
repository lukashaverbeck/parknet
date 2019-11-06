from projektkurs.tests.EventHandlerTest import EventHandlerTest

def othermethod(x):
    print("method2 "+str(x))

EventHandlerTest.registerInEvent(othermethod)

EventHandlerTest.runEvent("Command here")