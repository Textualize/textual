from __future__ import annotations

from functools import lru_cache

from inspect import signature, isawaitable
from typing import Any, Callable


@lru_cache(maxsize=2048)
def count_parameters(func: Callable) -> int:
    """Count the number of parameters in a callable"""
    return len(signature(func).parameters)


async def invoke(callback: Callable, *params: object) -> Any:
    """Invoke a callback with an arbitrary number of parameters.

    Args:
        callback (Callable): [description]

    Returns:
        Any: [description]
    """
    _rich_traceback_guard = True
    parameter_count = count_parameters(callback)
    result = callback(*params[:parameter_count])
    if isawaitable(result):
        result = await result
    return result
