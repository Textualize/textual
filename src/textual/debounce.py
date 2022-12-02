import asyncio
from functools import wraps
from typing import Any, Callable, Optional, ParamSpec

from .app import App
from .timer import Timer as TimerClass

P = ParamSpec("P")


def debounce(timeout: float) -> Callable[[Callable[P, Any]], Callable[P, None]]:
    """Debounce repeated events.

    If event handlers perform expensive operations, then it is sometimes desirable to
    limit the number of calls to the handler. The debounce decorartor will (re)start
    a timer for every event received and only call the handler if no events have occured
    in the time period provided.

    Args:
        timeout (float): the number of seconds to wait for repeated events.
    """

    def decorator(f: Callable[P, Any]) -> Callable[P, None]:
        timer: Optional[TimerClass] = None

        @wraps(f)
        async def wrapper(self: App, *args: P.args, **kwargs: P.kwargs) -> None:
            nonlocal timer
            if timer:
                timer.reset()
            else:
                timer = self.set_timer(
                    timeout, lambda: asyncio.create_task(f(self, *args, *kwargs))
                )

        return wrapper

    return decorator
