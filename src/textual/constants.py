"""
Constants that we might want to expose via the public API.

"""

from __future__ import annotations

import os

from typing_extensions import Final

from ._border import BORDER_CHARS

__all__ = ["BORDERS"]

get_environ = os.environ.get

DEVTOOLS_PORT_ENVIRON_VARIABLE = "TEXTUAL_CONSOLE_PORT"
DEFAULT_DEVTOOLS_PORT = 8081


def get_environ_bool(name: str) -> bool:
    """Check an environment variable switch.

    Args:
        name: Name of environment variable.

    Returns:
        `True` if the env var is "1", otherwise `False`.
    """
    has_environ = get_environ(name) == "1"
    return has_environ


def get_port_for_devtools() -> int:
    """Get the port to run the devtools on from the environment or the default."""
    try:
        return int(os.environ[DEVTOOLS_PORT_ENVIRON_VARIABLE])
    except (KeyError, ValueError):
        return DEFAULT_DEVTOOLS_PORT


BORDERS = list(BORDER_CHARS)

DEBUG: Final[bool] = get_environ_bool("TEXTUAL_DEBUG")

DRIVER: Final[str | None] = get_environ("TEXTUAL_DRIVER", None)

LOG_FILE: Final[str | None] = get_environ("TEXTUAL_LOG", None)
"""A last resort log file that appends all logs, when devtools isn't working."""
