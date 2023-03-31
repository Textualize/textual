from enum import Enum


class LogGroup(Enum):
    """A log group is a classification of the log message (*not* a level)."""

    UNDEFINED = 0  # Mainly for testing
    EVENT = 1
    DEBUG = 2
    INFO = 3
    WARNING = 4
    ERROR = 5
    PRINT = 6
    SYSTEM = 7
    LOGGING = 8
    WORKER = 9


class LogVerbosity(Enum):
    """Tags log messages as being verbose and potentially excluded from output."""

    NORMAL = 0
    HIGH = 1
