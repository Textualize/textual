from __future__ import annotations

import inspect
from typing import TYPE_CHECKING

import rich.repr
from rich.console import RenderableType

__all__ = ["log", "panic"]


from ._log import LogGroup, LogVerbosity, LogSeverity


@rich.repr.auto
class Logger:
    """A Textual logger."""

    def __init__(
        self,
        group: LogGroup = LogGroup.INFO,
        verbosity: LogVerbosity = LogVerbosity.NORMAL,
        severity: LogSeverity = LogSeverity.NORMAL,
    ) -> None:
        self._group = group
        self._verbosity = verbosity
        self._severity = severity

    def __rich_repr__(self) -> rich.repr.Result:
        yield self._group, LogGroup.INFO
        yield self._verbosity, LogVerbosity.NORMAL
        yield self._severity, LogSeverity.NORMAL

    def __call__(self, *args: object, **kwargs) -> None:
        from ._context import active_app

        app = active_app.get()
        caller = inspect.stack()[1]
        app._log(
            self._group,
            self._verbosity,
            self._severity,
            *args,
            _textual_calling_frame=caller,
            **kwargs,
        )

    def verbosity(self, verbose: bool) -> Logger:
        """Get a new logger with selective verbosity.

        Args:
            verbose (bool): True to use HIGH verbosity, otherwise NORMAL.

        Returns:
            Logger: New logger.
        """
        verbosity = LogVerbosity.HIGH if verbose else LogVerbosity.NORMAL
        return Logger(self._group, verbosity, LogSeverity.NORMAL)

    @property
    def verbose(self) -> Logger:
        """A verbose logger."""
        return Logger(self._group, LogVerbosity.HIGH)

    @property
    def critical(self) -> Logger:
        """A critical logger."""
        return Logger(self._group, self._verbosity, LogSeverity.CRITICAL)

    @property
    def event(self) -> Logger:
        """An event logger."""
        return Logger(LogGroup.EVENT)

    @property
    def debug(self) -> Logger:
        """A debug logger."""
        return Logger(LogGroup.DEBUG)

    @property
    def info(self) -> Logger:
        """An info logger."""
        return Logger(LogGroup.INFO)

    @property
    def warning(self) -> Logger:
        """An info logger."""
        return Logger(LogGroup.WARNING)

    @property
    def error(self) -> Logger:
        """An error logger."""
        return Logger(LogGroup.ERROR)

    @property
    def system(self) -> Logger:
        """A system logger."""
        return Logger(LogGroup.SYSTEM)


log = Logger()


def panic(*args: RenderableType) -> None:
    from ._context import active_app

    app = active_app.get()
    app.panic(*args)
