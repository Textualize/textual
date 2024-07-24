"""
Functions related to debugging.
"""

from . import constants


def get_caller_file_and_line() -> str | None:
    """Get the caller filename and line, if in debug mode, otherwise return `None`:

    Returns:
        Path and file if `constants.DEBUG==True`
    """
    import inspect

    if not constants.DEBUG:
        return None
    try:
        current_frame = inspect.currentframe()
        caller_frame = inspect.getframeinfo(current_frame.f_back.f_back)
        return f"{caller_frame.filename}:{caller_frame.lineno}"
    except Exception:
        return None
