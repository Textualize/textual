"""
A Textual Logging handler.

If there is an active Textual app, then log messages will go via the app (and logged via textual console).

If there is *no* active app, then log messages will go to stderr or stdout, depending on configuration.
"""

import sys
from logging import Handler, LogRecord

from ._context import active_app


class TextualHandler(Handler):
    """A Logging handler for Textual apps."""

    def __init__(self, stderr: bool = True, stdout: bool = False) -> None:
        """Initialize a Textual logging handler.

        Args:
            stderr: Log to stderr when there is no active app.
            stdout: Log to stdout when there is no active app.
        """
        super().__init__()
        self._stderr = stderr
        self._stdout = stdout

    def emit(self, record: LogRecord) -> None:
        """Invoked by logging."""
        message = self.format(record)
        try:
            app = active_app.get()
        except LookupError:
            if self._stderr:
                print(message, file=sys.stderr)
            elif self._stdout:
                print(message, file=sys.stdout)
        else:
            app.log.logging(message)
