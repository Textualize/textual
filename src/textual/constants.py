"""
Constants that we might want to expose via the public API.

"""

"""
A number of app level constants where the value is pulled from environment variables.
"""

import os
from typing import Final

get_environ = os.environ.get


def get_environ_bool(name: str) -> bool:
    """Check an environment variable switch.

    Args:
        name: Name of environment variable.

    Returns:
        True if the env var is "1", otherwise False.
    """
    has_environ = os.environ.get(name) == "1"
    return has_environ


from ._border import BORDER_CHARS

__all__ = ["BORDERS"]


BORDERS = list(BORDER_CHARS)

DEBUG: Final[bool] = get_environ_bool("TEXTUAL_DEBUG")
