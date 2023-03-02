from __future__ import annotations

import asyncio
from functools import lru_cache
from inspect import isawaitable, signature
from typing import TYPE_CHECKING, Any, Callable

from . import active_app

if TYPE_CHECKING:
    from .app import App

# Maximum seconds before warning about a slow callback
INVOKE_TIMEOUT_WARNING = 3


@lru_cache(maxsize=2048)
def count_parameters(func: Callable) -> int:
    """Count the number of parameters in a callable"""
    return len(signature(func).parameters)


async def _invoke(callback: Callable, *params: object) -> Any:
    """Invoke a callback with an arbitrary number of parameters.

    Args:
        callback: The callable to be invoked.

    Returns:
        The return value of the invoked callable.
    """
    _rich_traceback_guard = True
    parameter_count = count_parameters(callback)
    result = callback(*params[:parameter_count])
    if isawaitable(result):
        result = await result
    return result


async def invoke(callback: Callable, *params: object) -> Any:
    """Invoke a callback with an arbitrary number of parameters.

    Args:
        callback: The callable to be invoked.

    Returns:
        The return value of the invoked callable.
    """

    app: App | None
    try:
        app = active_app.get()
    except LookupError:
        # May occur if this method is called outside of an app context (i.e. in a unit test)
        app = None

    if app is not None and "debug" in app.features:
        # In debug mode we will warn about callbacks that may be stuck
        def log_slow() -> None:
            """Log a message regarding a slow callback."""
            assert app is not None
            app.log.warning(
                f"Callback {callback} is still pending after {INVOKE_TIMEOUT_WARNING} seconds"
            )

        call_later_handle = asyncio.get_running_loop().call_later(
            INVOKE_TIMEOUT_WARNING, log_slow
        )
        try:
            return await _invoke(callback, *params)
        finally:
            call_later_handle.cancel()
    else:
        return await _invoke(callback, *params)
