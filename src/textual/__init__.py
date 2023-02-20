from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Callable

import rich.repr
from rich.console import RenderableType

from ._context import active_app
from ._log import LogGroup, LogVerbosity

if TYPE_CHECKING:
    from typing_extensions import TypeAlias

__all__ = ["log", "panic", "__version__"]  # type: ignore


LogCallable: TypeAlias = "Callable"


def __getattr__(name: str) -> str:
    """Lazily get the version from whatever API is available."""
    if name == "__version__":
        try:
            from importlib.metadata import version
        except ImportError:
            import pkg_resources

            return pkg_resources.get_distribution("textual").version
        else:
            return version("textual")
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


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

    def __rich_repr__(self) -> rich.repr.Result:
        yield self._group, LogGroup.INFO
        yield self._verbosity, LogVerbosity.NORMAL

    def __call__(self, *args: object, **kwargs) -> None:
        try:
            app = active_app.get()
        except LookupError:
            print_args = (*args, *[f"{key}={value!r}" for key, value in kwargs.items()])
            print(*print_args)
            return
        if app.devtools is None or not app.devtools.is_connected:
            return

        current_frame = inspect.currentframe()
        assert current_frame is not None
        previous_frame = current_frame.f_back
        assert previous_frame is not None
        caller = inspect.getframeinfo(previous_frame)

        _log = self._log or app._log
        try:
            _log(
                self._group,
                self._verbosity,
                caller,
                *args,
                **kwargs,
            )
        except LoggerError:
            # If there is not active app, try printing
            print_args = (*args, *[f"{key}={value!r}" for key, value in kwargs.items()])
            print(*print_args)

    def verbosity(self, verbose: bool) -> Logger:
        """Get a new logger with selective verbosity.

        Args:
            verbose: True to use HIGH verbosity, otherwise NORMAL.

        Returns:
            New logger.
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
