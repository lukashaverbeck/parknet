# This module contains utility classes and functions that may be used
# throughout the whole project and cannot be assigned to single modules.
#
# author: @lukashaverbeck
# version: 2.0 (29.12.2019)


class Singleton:
    """ helper class ensuring that classes decorated with it can only be instantiated one single time so that
        the same object can be accessed at multiple locations in the code without having to pass it around
    """

    def __init__(self, decorated):
        """ initializes the Singleton """

        self.object = None
        self.decorated = decorated

    def instance(self, *args, **kwargs):
        """ gets the same instance of a particluar class every time it is called

            returns:
                object: singleton of the class for which the method is called
        """

        # check if an instance has to be created
        if self.object is None:
            self.object = self.decorated(*args, **kwargs)
            return self.object
        
        return self.object

    def __call__(self):
        raise TypeError("Singletons must be accessed through `instance()`")

    def __instancecheck__(self, instance):
        return isinstance(instance, self.decorated)
