import asyncio
from functools import wraps
from typing import Callable, Optional

from .app import App
from .timer import Timer as TimerClass


def debounce(timeout: float) -> Callable:
    """Debounce repeated events.

    If event handlers perform expensive operations, then it is sometimes desirable to
    limit the number of calls to the handler. The debounce decorartor will (re)start
    a timer for every event received and only call the handler if no events have occured
    in the time period provided.

    Args:
        timeout (float): the number of seconds to wait for repeated events.
    """

    def decorator(f: Callable) -> Callable:
        timer: Optional[TimerClass] = None

        @wraps(f)
        async def wrapper(self: App, *args, **kwargs) -> None:
            nonlocal timer
            if timer:
                timer.reset()
            else:
                timer = self.set_timer(
                    timeout, lambda: asyncio.create_task(f(self, *args, *kwargs))
                )

        return wrapper

    return decorator
