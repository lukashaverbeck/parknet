from threading import Thread
from typing import Callable, Any


def threaded(name: str, daemon: bool = True) -> Callable:
    """ Decorator factory for executing a function in its own thread every time it is called.

    Whenever a function is decorated with ``@threaded(...)``, it will be started in its own thread every time it is
    called.

    Notes:
        A ``@threaded`` function should return values other than None since it is run in its own thread.

    Args:
        name: Name of the thread the function is executed in.
        daemon: Boolean whether the thread is daemonic.

    Returns:
        The according decorator function.
    """

    def decorator(function: Callable[[Any], None]) -> Callable:
        def execute_in_thread(*args, **kwargs) -> None:
            thread = Thread(target=lambda: function(*args, **kwargs), name=name, daemon=daemon)
            thread.start()

        return execute_in_thread

    return decorator
