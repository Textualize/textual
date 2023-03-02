from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, cast

from .._log import LogGroup, LogVerbosity
from .client import DevtoolsLog

if TYPE_CHECKING:
    from .client import DevtoolsClient


class StdoutRedirector:
    """
    A write-only file-like object which redirects anything written to it to the devtools
    instance associated with the given Textual application. Used within Textual to redirect
    data written using `print` (or any other stdout writes) to the devtools and/or to the
    log file.
    """

    def __init__(self, devtools: DevtoolsClient) -> None:
        """
        Args:
            devtools: The running Textual app instance.
            log_file: The log file for the Textual App.
        """
        self.devtools = devtools
        self._buffer: list[DevtoolsLog] = []

    def write(self, string: str) -> None:
        """Write the log string to the internal buffer. If the string contains
        a newline character `\n`, the whole string will be buffered and then the
        buffer will be flushed immediately after.

        Args:
            string: The string to write to the buffer.
        """

        if not self.devtools.is_connected:
            return

        current_frame = inspect.currentframe()
        assert current_frame is not None
        previous_frame = current_frame.f_back
        assert previous_frame is not None
        caller = inspect.getframeinfo(previous_frame)

        self._buffer.append(DevtoolsLog(string, caller=caller))

        # By default, `print` adds a "\n" suffix which results in a buffer
        # flush. You can choose a different suffix with the `end` parameter.
        # If you modify the `end` parameter to something other than "\n",
        # then `print` will no longer flush automatically. However, if a
        # string you are printing contains a "\n", that will trigger
        # a flush after that string has been buffered, regardless of the value
        # of `end`.
        if "\n" in string:
            self.flush()

    def flush(self) -> None:
        """Flush the buffer. This will send all buffered log messages to
        the devtools server and the log file. In the case of the devtools,
        where possible, log messages will be batched and sent as one.
        """
        self._write_to_devtools()
        self._buffer.clear()

    def _write_to_devtools(self) -> None:
        """Send the contents of the buffer to the devtools."""
        if not self.devtools.is_connected:
            return

        log_batch: list[DevtoolsLog] = []
        for log in self._buffer:
            end_of_batch = log_batch and (
                log_batch[-1].caller.filename != log.caller.filename
                or log_batch[-1].caller.lineno != log.caller.lineno
            )
            if end_of_batch:
                self._log_devtools_batched(log_batch)
                log_batch.clear()
            log_batch.append(log)
        if log_batch:
            self._log_devtools_batched(log_batch)

    def _log_devtools_batched(self, log_batch: list[DevtoolsLog]) -> None:
        """Write a single batch of logs to devtools. A batch means contiguous logs
        which have been written from the same line number and file path.
        A single `print` call may correspond to multiple writes.
        e.g. `print("a", "b", "c")` is 3 calls to `write`, so we batch
        up these 3 write calls since they come from the same location, so that
        they appear inside the same log message in the devtools window
        rather than a single `print` statement resulting in 3 separate
        logs being displayed.

        Args:
            log_batch: A batch of logs to send to the
                devtools server as one. Log content will be joined together.
        """

        # This code is only called via stdout.write, and so by this point we know
        # that the log message content is a string. The cast below tells mypy this.
        batched_log = "".join(cast(str, log.objects_or_string) for log in log_batch)
        batched_log = batched_log.rstrip()
        self.devtools.log(
            DevtoolsLog(batched_log, caller=log_batch[-1].caller),
            LogGroup.PRINT,
            LogVerbosity.NORMAL,
        )
