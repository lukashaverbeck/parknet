def testhere(x):
    print("arg was "+str(x))

methods = []
args = ["unset"]


class EventHandlerTest:
    def runEvent(message):
        print ("Executing")
        for item in methods:
            item['f'](message)
    def registerInEvent(methodName):
        methods.append({'f': methodName, 'a': args})
        ##print("Registered" + methodName)

EventHandlerTest.registerInEvent(testhere)