import timeit
from typing import Callable, Any


def measure_execution_time(function: Callable) -> Callable:
    """ Decorator measuring the execution time of a function every time it is called.

    This function wraps and returns a function that calls ``function`` and measures the duration it takes to execute.
    The duration is then printed. The functionality of ``function`` is not affected.

    Notes:
        This function is intended to be used as a decorator.

    Args:
        function: Function whose execution time is to be measured when called.

    Returns:
        Function calling the decorated function and measuring its execution time.
    """

    def execute(*args, **kwargs) -> Any:
        """ Calls the function and measures its execution time.

        This function measures the time ``function`` takes to execute by taking the differences of times before and
        after its execution. The result is the printed with a 5 point decimal precision.
        The result of ``function`` as well as its arguments are not changed.

        Args:
            *args: Arguments, the decorated function is called with.
            **kwargs: Keyword arguments, the decorated function is called with.

        Returns:
            Result of the execution of the decorated function.
        """

        # measure time before and after executing the decorated function
        start = timeit.default_timer()
        result = function(*args, **kwargs)
        end = timeit.default_timer()

        # print elapsed time
        print(f"{function.__name__} took {(end - start):.5f}ms to execute")

        # return result of executing the decorated function
        return result

    return execute
