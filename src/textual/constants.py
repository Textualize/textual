"""
Constants that we might want to expose via the public API.

"""

from __future__ import annotations

import os

from typing_extensions import Final

from ._border import BORDER_CHARS

__all__ = ["BORDERS"]

get_environ = os.environ.get


def get_environ_bool(name: str) -> bool:
    """Check an environment variable switch.

    Args:
        name: Name of environment variable.

    Returns:
        `True` if the env var is "1", otherwise `False`.
    """
    has_environ = get_environ(name) == "1"
    return has_environ


def get_environ_int(name: str, default: int) -> int:
    """Retrieves an integer environment variable.

    Args:
        name: Name of environment variable.
        default: The value to use if the value is not set, or set to something other
            than a valid integer.

    Returns:
        The integer associated with the environment variable if it's set to a valid int
            or the default value otherwise.
    """
    try:
        return int(get_environ(name, default))
    except ValueError:
        return default


BORDERS = list(BORDER_CHARS)

DEBUG: Final[bool] = get_environ_bool("TEXTUAL_DEBUG")

DRIVER: Final[str | None] = get_environ("TEXTUAL_DRIVER", None)

LOG_FILE: Final[str | None] = get_environ("TEXTUAL_LOG", None)
"""A last resort log file that appends all logs, when devtools isn't working."""


DEVTOOLS_PORT_ENVIRON_VARIABLE: Final[str] = "TEXTUAL_CONSOLE_PORT"
"""The name of the environment variable that sets the port for the devtools."""
DEFAULT_DEVTOOLS_PORT: Final[int] = 8081
"""The default port to use for the devtools."""
DEVTOOLS_PORT: Final[int] = get_environ_int(
    DEVTOOLS_PORT_ENVIRON_VARIABLE, DEFAULT_DEVTOOLS_PORT
)
"""Constant with the port that the devtools will connect to."""
