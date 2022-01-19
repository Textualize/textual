import re

_match_duration = re.compile(r"^(-?\d+\.?\d*)(s|ms)$").match


class DurationError(Exception):
    """
    Exception indicating a general issue with a CSS duration.
    """


class DurationParseError(DurationError):
    """
    Indicates a malformed duration string that could not be parsed.
    """


def _duration_as_seconds(duration: str) -> float:
    """
    Args:
        duration (str): A string of the form ``"2s"`` or ``"300ms"``, representing 2 seconds and
            300 milliseconds respectively. If no unit is supplied, e.g. ``"2"``, then the duration is
            assumed to be in seconds.
    Raises:
        DurationParseError: If the argument ``duration`` is not a valid duration string.
    Returns:
        float: The duration in seconds.

    """
    match = _match_duration(duration)

    if match:
        value, unit_name = match.groups()
        value = float(value)
        if unit_name == "ms":
            duration_secs = value / 1000
        else:
            duration_secs = value
    else:
        try:
            duration_secs = float(duration)
        except ValueError:
            raise DurationParseError(
                f"{duration!r} is not a valid duration."
            ) from ValueError

    return duration_secs
