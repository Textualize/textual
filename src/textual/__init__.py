from __future__ import annotations

import sys
import inspect
from typing import Callable, TYPE_CHECKING

import rich.repr
from rich.console import RenderableType

__all__ = ["log", "panic"]


from ._context import active_app
from ._log import LogGroup, LogVerbosity

if TYPE_CHECKING:
    from .app import App

if sys.version_info >= (3, 10):
    from typing import TypeAlias
else:  # pragma: no cover
    from typing_extensions import TypeAlias


LogCallable: TypeAlias = "Callable"


class LoggerError(Exception):
    """Raised when the logger failed."""


@rich.repr.auto
class Logger:
    """A Textual logger."""

    def __init__(
        self,
        log_callable: LogCallable | None,
        group: LogGroup = LogGroup.INFO,
        verbosity: LogVerbosity = LogVerbosity.NORMAL,
    ) -> None:
        self._log = log_callable
        self._group = group
        self._verbosity = verbosity

    @property
    def log(self) -> LogCallable:
        if self._log is None:
            try:
                app = active_app.get()
            except LookupError:
                raise LoggerError("Unable to log without an active app.") from None
            return app._log
        return self._log

    def __rich_repr__(self) -> rich.repr.Result:
        yield self._group, LogGroup.INFO
        yield self._verbosity, LogVerbosity.NORMAL

    def __call__(self, *args: object, **kwargs) -> None:
        caller = inspect.stack()[1]
        try:
            self.log(
                self._group,
                self._verbosity,
                *args,
                _textual_calling_frame=caller,
                **kwargs,
            )
        except LoggerError:
            # If there is not active app, try printing
            print_args = (*args, *[f"{key}={value!r}" for key, value in kwargs.items()])
            print(*print_args)

    def verbosity(self, verbose: bool) -> Logger:
        """Get a new logger with selective verbosity.

        Args:
            verbose (bool): True to use HIGH verbosity, otherwise NORMAL.

        Returns:
            Logger: New logger.
        """
        verbosity = LogVerbosity.HIGH if verbose else LogVerbosity.NORMAL
        return Logger(self._log, self._group, verbosity)

    @property
    def verbose(self) -> Logger:
        """A verbose logger."""
        return Logger(self._log, self._group, LogVerbosity.HIGH)

    @property
    def event(self) -> Logger:
        """Logs events."""
        return Logger(self._log, LogGroup.EVENT)

    @property
    def debug(self) -> Logger:
        """Logs debug messages."""
        return Logger(self._log, LogGroup.DEBUG)

    @property
    def info(self) -> Logger:
        """Logs information."""
        return Logger(self._log, LogGroup.INFO)

    @property
    def warning(self) -> Logger:
        """Logs warnings."""
        return Logger(self._log, LogGroup.WARNING)

    @property
    def error(self) -> Logger:
        """Logs errors."""
        return Logger(self._log, LogGroup.ERROR)

    @property
    def system(self) -> Logger:
        """Logs system information."""
        return Logger(self._log, LogGroup.SYSTEM)


log = Logger(None)


def panic(*args: RenderableType) -> None:
    from ._context import active_app

    app = active_app.get()
    app.panic(*args)
