import re

_match_duration = re.compile(r"^(-?\d+\.?\d*)(s|ms)?$").match


class DurationError(Exception):
    pass


class DurationParseError(DurationError):
    pass


def _duration_as_seconds(duration: str) -> float:
    """
    Args:
        duration (str): A string of the form "2s" or "300ms", representing 2 seconds and 300 milliseconds respectively.

    Returns (float): The duration converted to seconds.

    """
    match = _match_duration(duration)
    if not match:
        raise DurationParseError(f"'{duration}' is not a valid duration.")

    value, unit_name = match.groups()
    value = float(value)
    if unit_name == "ms":
        duration_secs = value / 1000
    else:
        duration_secs = value
    return duration_secs
