from __future__ import annotations

from functools import lru_cache

from inspect import signature, isawaitable, Parameter
from typing import Any, Callable


@lru_cache(maxsize=2048)
def count_parameters(func: Callable) -> tuple[int, bool]:
    """Count the number of parameters in a callable, and checks if the last positional one is a "capture all"

    Args:
        func (Callable): a callable
    Returns:
        tuple[int, bool]: the number of parameters, and a boolean that is `True` only if
            the last positional parameter is a "capture all" (i.e. `*args`)
    """
    callable_signature = signature(func)
    callable_parameters = callable_signature.parameters
    parameters_count = len(callable_parameters)
    has_capture_all = parameters_count > 0 and any(
        (
            parameter.kind is Parameter.VAR_POSITIONAL
            for parameter in callable_parameters.values()
        )
    )
    return parameters_count, has_capture_all


async def invoke(callback: Callable, *params: object) -> Any:
    """Invoke a callback with an arbitrary number of parameters.

    Args:
        callback (Callable): [description]

    Returns:
        Any: [description]
    """
    _rich_traceback_guard = True
    parameter_count, has_capture_all = count_parameters(callback)
    # If the target has a "capture all" argument we simply inject everything,
    # otherwise we only inject the number of arguments expected by the callable:
    parameters = params if has_capture_all else params[:parameter_count]

    result = callback(*parameters)
    if isawaitable(result):
        result = await result
    return result
