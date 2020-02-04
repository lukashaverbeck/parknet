# This module contains utility classes and functions that may be used
# throughout the whole project and cannot be assigned to single modules.
#
# version: 1.0 (02.01.2019)

from threading import Thread


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
        """ ensures a singleton class not initialized directly

            Raises:
                TypeError: when trying to directly initialize a singleton class
        """

        raise TypeError("Singletons must be accessed through `instance()`")

    def __instancecheck__(self, instance):
        return isinstance(instance, self.decorated)


def threaded(func):
    """ allows to call a function in its own thread by decorating that function with @threaded
        NOTE this function does not start the thread directly but at the time the decorated function is called

        Args:
            func (function): function to be executed in its own thread

        Returns:
            function: decorated function
    """

    def start_threaded_function(*args, **kwargs):
        thread = Thread(target=lambda: func(*args, **kwargs))
        thread.start()

    return start_threaded_function
