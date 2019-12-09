class Singleton:
    """ helper class ensuring that classes decorated with it can only be instantiated one single time """

    def __init__(self, decorated):
        self.__instance = None
        self.__decorated = decorated

    def instance(self):
        """ gets the same instance of a particluar class every time it is called

            returns:
                object: any object decorated with `Singleton` but the same instance of it every time
        """

        if self.__instance is None:
            self.__instance = self.__decorated()
            return self.__instance
        
        return self.__instance

    def __call__(self):
        raise TypeError("Singletons must be accessed through `instance()`.")

    def __instancecheck__(self, instance):
        return isinstance(instance, self.__decorated)
