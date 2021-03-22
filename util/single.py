from typing import Optional


class _Single:
    def __init__(self, cls: type):
        self._cls: type = cls


class SingleUse(_Single):
    """ Decorator ensuring that an instance of a class is only instantiated a single time within memory space.

    The first a class decorated with ``@SingleUse`` is called, it returns an instance of the class. Every other time an
    instance of the class is requested, an exception is raised.
    For retrieving an instance of a ``SingleUse`` class, the usual syntax for creating objects can be used.

    Notes:
        This class is intended to be used as a class decorator.
    """

    def __init__(self, cls: type):
        super().__init__(cls)
        self._instantiated: bool = False

    def __call__(self, *args, **kwargs):
        if self._instantiated:  # raise exception if there already is an instance
            raise Exception(f"Creating multiple instances of {self._cls.__name__} is not allowed.")
        else:  # otherwise return a new instance and mark the class as instantiated
            self._instantiated = True
            return self._cls(*args, **kwargs)


class Singleton(_Single):
    """ Decorator ensuring that there can be only one instance of a class within memory space.

    Whenever a class decorated with ``@Singleton`` is called, the same instance of the class is returned.
    For retrieving an instance of a ``Singleton`` class, the usual syntax for creating objects can be used.

    Notes:
        This class is intended to be used as a class decorator.
    """

    def __init__(self, cls: type):
        super().__init__(cls)
        self._instance: Optional[object] = None

    def __call__(self, *args, **kwargs):
        # create an instance if there is none already
        if self._instance is None:
            self._instance = self._cls(*args, **kwargs)

        return self._instance
