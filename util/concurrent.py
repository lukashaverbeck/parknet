import math
import time
from typing import Any, Callable

import util


def stabilized_concurrent(name: str, min_delay: float, max_delay: float, steps: int, daemon: bool = True) -> Callable:
    """ Decorator factory for concurrently executing a function with dynamic delays in between.

        Whenever a function is decorated with ``@stabilized_concurrent(...)``, it will be executed concurrently with
        dynamically changing delays in between two executions. The longer the execution has been stable, the longer the
        delay.
        An execution was stable exactly if the decorated function returned True.

        Notes:
            A ``@stabilized_concurrent`` function cannot return Values other than None since it is run in its own
            thread.

        Args:
            name: Name of the thread the function is executed in.
            min_delay: Lower bound for the dynamic delay.
            max_delay: Upper bound for the dynamic delay.
            steps: Number of stable executions to reach the maximum delay.
            daemon: Boolean whether the thread in which the function is executed is daemonic.

        Returns:
            The according decorator function.
        """

    # the minimum delay must be less than the maximum delay
    assert 0 < min_delay < max_delay, "Minimum delay must be positive and less than max delay."

    # there must be at least one step from minimum to maximum delay
    assert steps > 0, "It must take at least one step to reach the maximum delay."

    def calc_delay(stable_intervals: int) -> float:
        """ Calculates the delay before the next execution based on the number of consecutive stable executions.

        The delay d is defined as min_delay * exp(stable_intervals * ln(max_delay / min_delay) / steps) normally but is
        at maximum ``max_delay``. For 0 stable intervals the delay is ``min_delay``. After ``steps`` stable intervals,
        the delay is ``max_delay``.

        Args:
            stable_intervals: Number of consecutive stable executions.

        Returns:
            The delay to wait before the next execution in seconds.
        """

        return min(max_delay, min_delay * math.exp(stable_intervals * math.log(max_delay / min_delay) / steps))

    def decorator(function: Callable[[Any], bool]) -> Callable:
        @util.threaded(name, daemon)
        def concurrent_execution(*args, **kwargs) -> None:
            """ Concurrently executes the decorated function with dynamically calculated delays in between.

            The delay is calculated based on the number of consecutive stable executions of the function.
            The execution of the decorated function was stable exactly if the function returns ``True``.

            Args:
                *args: Arguments, the decorated function is called with.
                **kwargs: Keyword arguments, the decorated function is called with.
            """

            # initially there have been no stable executions
            stable_intervals = 0

            while True:
                # execute the decorated function and save the result
                stable = function(*args, **kwargs)

                # the decorated function must return a Boolean
                assert stable is True or stable is False, f"A stabilized concurrent function must return a Boolean " \
                                                          f"but {function.__name__}(...) did not."

                # calculate a dynamic delay and stop the execution for the corresponding duration
                delay = calc_delay(stable_intervals)
                time.sleep(delay)

                # update number of stable executions accordingly to the result of the latest execution
                stable_intervals = stable_intervals + 1 if stable else 0

        return concurrent_execution

    return decorator
