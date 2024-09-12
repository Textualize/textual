"""
Functions related to debugging.
"""

from __future__ import annotations

from textual import constants


def get_caller_file_and_line() -> str | None:
    """Get the caller filename and line, if in debug mode, otherwise return `None`:

    Returns:
        Path and file if `constants.DEBUG==True`
    """

    if not constants.DEBUG:
        return None
    import inspect

    try:
        current_frame = inspect.currentframe()
        caller_frame = inspect.getframeinfo(current_frame.f_back.f_back)
        return f"{caller_frame.filename}:{caller_frame.lineno}"
    except Exception:
        return None
