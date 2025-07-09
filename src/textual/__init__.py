"""
The root Textual module.

Exposes some commonly used symbols.

"""

from __future__ import annotations

import inspect
import weakref
from typing import TYPE_CHECKING, Callable

import rich.repr

from textual import constants
from textual._context import active_app
from textual._log import LogGroup, LogVerbosity
from textual._on import on
from textual._work_decorator import work

if TYPE_CHECKING:
    from typing_extensions import TypeAlias

__all__ = [
    "__version__",  # type: ignore
    "log",
    "on",
    "work",
]


LogCallable: TypeAlias = "Callable"


if TYPE_CHECKING:
    from importlib.metadata import version

    from textual.app import App

    __version__ = version("textual")
    """The version of Textual."""

else:

    def __getattr__(name: str) -> str:
        """Lazily get the version."""
        if name == "__version__":
            from importlib.metadata import version

            return version("textual")
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


class LoggerError(Exception):
    """Raised when the logger failed."""


@rich.repr.auto
class Logger:
    """A [logger class](/guide/devtools/#logging-handler) that logs to the Textual [console](/guide/devtools#console)."""

    def __init__(
        self,
        log_callable: LogCallable | None,
        group: LogGroup = LogGroup.INFO,
        verbosity: LogVerbosity = LogVerbosity.NORMAL,
        app: App | None = None,
    ) -> None:
        self._log = log_callable
        self._group = group
        self._verbosity = verbosity
        self._app = None if app is None else weakref.ref(app)

    @property
    def app(self) -> App | None:
        """The associated application, or `None` if there isn't one."""
        return None if self._app is None else self._app()

    def __rich_repr__(self) -> rich.repr.Result:
        yield self._group, LogGroup.INFO
        yield self._verbosity, LogVerbosity.NORMAL

    def __call__(self, *args: object, **kwargs) -> None:
        if constants.LOG_FILE:
            output = " ".join(str(arg) for arg in args)
            if kwargs:
                key_values = " ".join(
                    f"{key}={value!r}" for key, value in kwargs.items()
                )
                output = f"{output} {key_values}" if output else key_values

            with open(constants.LOG_FILE, "a", encoding="utf-8") as log_file:
                print(output, file=log_file)

        app = self.app
        if app is None:
            try:
                app = active_app.get()
            except LookupError:
                if constants.DEBUG:
                    print_args = (
                        *args,
                        *[f"{key}={value!r}" for key, value in kwargs.items()],
                    )
                    print(*print_args)
                return
        if not app._is_devtools_connected:
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
            if constants.DEBUG:
                print_args = (
                    *args,
                    *[f"{key}={value!r}" for key, value in kwargs.items()],
                )
                print(*print_args)

    def verbosity(self, verbose: bool) -> Logger:
        """Get a new logger with selective verbosity.

        Args:
            verbose: True to use HIGH verbosity, otherwise NORMAL.

        Returns:
            New logger.
        """
        verbosity = LogVerbosity.HIGH if verbose else LogVerbosity.NORMAL
        return Logger(self._log, self._group, verbosity, app=self.app)

    @property
    def verbose(self) -> Logger:
        """A verbose logger."""
        return Logger(self._log, self._group, LogVerbosity.HIGH, app=self.app)

    @property
    def event(self) -> Logger:
        """Logs events."""
        return Logger(self._log, LogGroup.EVENT, app=self.app)

    @property
    def debug(self) -> Logger:
        """Logs debug messages."""
        return Logger(self._log, LogGroup.DEBUG, app=self.app)

    @property
    def info(self) -> Logger:
        """Logs information."""
        return Logger(self._log, LogGroup.INFO, app=self.app)

    @property
    def warning(self) -> Logger:
        """Logs warnings."""
        return Logger(self._log, LogGroup.WARNING, app=self.app)

    @property
    def error(self) -> Logger:
        """Logs errors."""
        return Logger(self._log, LogGroup.ERROR, app=self.app)

    @property
    def system(self) -> Logger:
        """Logs system information."""
        return Logger(self._log, LogGroup.SYSTEM, app=self.app)

    @property
    def logging(self) -> Logger:
        """Logs from stdlib logging module."""
        return Logger(self._log, LogGroup.LOGGING, app=self.app)

    @property
    def worker(self) -> Logger:
        """Logs worker information."""
        return Logger(self._log, LogGroup.WORKER, app=self.app)


log = Logger(None)
"""Global logger that logs to the currently active app.

Example:
    ```python
    from textual import log
    log(locals())
    ```

!!! note
    This logger will only work if there is an active app in the current thread.
    Use `app.log` to write logs from a thread without an active app.


"""
