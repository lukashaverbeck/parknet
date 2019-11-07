def testhere(x):
    print("arg was "+str(x))

methods = []
args = ["unset"]


class EventHandlerTest:
    def runEvent(message):
        print ("Executing")
        for item in methods:
            print(item["a"])
            item['f'](message)
    def registerInEvent(methodName):
        methods.append({'f': methodName, 'a': args})
        ##print("Registered" + methodName)

EventHandlerTest.registerInEvent(testhere)
#EventHandlerTest.runEvent("Hello test123")