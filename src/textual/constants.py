"""
Constants that we might want to expose via the public API.
"""

from __future__ import annotations

import os

from typing_extensions import Final

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
        return int(os.environ[name])
    except KeyError:
        return default
    except ValueError:
        return default


DEBUG: Final[bool] = get_environ_bool("TEXTUAL_DEBUG")
"""Enable debug mode."""

DRIVER: Final[str | None] = get_environ("TEXTUAL_DRIVER", None)
"""Import for replacement driver."""

FILTERS: Final[str] = get_environ("TEXTUAL_FILTERS", "")
"""A list of filters to apply to renderables."""

LOG_FILE: Final[str | None] = get_environ("TEXTUAL_LOG", None)
"""A last resort log file that appends all logs, when devtools isn't working."""

DEVTOOLS_HOST: Final[str] = get_environ("TEXTUAL_DEVTOOLS_HOST", "127.0.0.1")
"""The host where textual console is running."""

DEVTOOLS_PORT: Final[int] = get_environ_int("TEXTUAL_DEVTOOLS_PORT", 8081)
"""Constant with the port that the devtools will connect to."""

SCREENSHOT_DELAY: Final[int] = get_environ_int("TEXTUAL_SCREENSHOT", -1)
"""Seconds delay before taking screenshot."""

PRESS: Final[str] = get_environ("TEXTUAL_PRESS", "")
"""Keys to automatically press."""

SHOW_RETURN: Final[bool] = get_environ_bool("TEXTUAL_SHOW_RETURN")
"""Write the return value on exit."""

MAX_FPS: Final[int] = get_environ_int("TEXTUAL_FPS", 60)
"""Maximum frames per second for updates."""

COLOR_SYSTEM: Final[str | None] = get_environ("TEXTUAL_COLOR_SYSTEM", "auto")
"""Force color system override"""
