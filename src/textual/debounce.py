import asyncio
from functools import wraps
from typing import Callable, Optional

from .app import App
from .timer import Timer as TimerClass


def debounce(timeout: float) -> Callable:
    def decorator(f: Callable) -> Callable:
        timer: Optional[TimerClass] = None

        @wraps(f)
        async def wrapper(self: App, *args, **kwargs) -> None:
            nonlocal timer
            if timer:
                timer.stop_no_wait()
            timer = self.set_timer(
                timeout, lambda: asyncio.create_task(f(self, *args, *kwargs))
            )

        return wrapper

    return decorator
