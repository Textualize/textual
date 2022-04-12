from __future__ import annotations

import inspect
from typing import TYPE_CHECKING
from textual.devtools.client import DevtoolsLog

if TYPE_CHECKING:
    from textual.devtools.client import DevtoolsClient


class DevtoolsRedirector:
    """
    A file-like object which redirects anything written to it to the devtools instance
    associated with the given Textual application. Used within Textual to redirect data
    written using `print` to the devtools.
    """

    def __init__(self, devtools: DevtoolsClient) -> None:
        """
        Args:
            devtools (DevtoolsClient): The running Textual app instance.
        """
        self.devtools = devtools
        self._buffer: list[DevtoolsLog] = []

    def write(self, string: str) -> None:
        """Write the log string to the internal buffer. If the string contains
        a newline character `\n`, the whole string will be buffered and then the
        buffer will be flushed immediately after.

        Args:
            string (str): The string to write to the buffer.
        """
        caller = inspect.stack()[1]
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
        the devtools server. Where possible, log messages will be batched
        and sent as one.
        """
        log_batch: list[DevtoolsLog] = []
        for log in self._buffer:
            end_of_batch = (
                log_batch
                and log_batch[-1].caller.filename != log.caller.filename
                and log_batch[-1].caller.lineno != log.caller.lineno
            )
            if end_of_batch:
                self._log_batched(log_batch)
                log_batch.clear()
            log_batch.append(log)

        if log_batch:
            self._log_batched(log_batch)

        self._buffer.clear()

    def _log_batched(self, log_batch: list[DevtoolsLog]) -> None:
        """Write a single batch of logs. A batch means contiguous logs
        which have been written from the same line number and file path.
        A single `print` call may correspond to multiple writes.
        e.g. `print("a", "b", "c")` is 3 calls to `write`, so we batch
        up these calls if they come from the same location in code, so that
        they appear inside the same log message in the devtools window
        rather than a single `print` statement resulting in 3 separate
        logs being displayed.

        Args:
            log_batch (list[DevtoolsLog]): A batch of logs to send to the
                devtools server as one. Log content will be joined together.
        """
        batched_log = "".join(log.objects_or_string for log in log_batch)
        batched_log = batched_log.rstrip()
        if self.devtools.is_connected:
            self.devtools.log(DevtoolsLog(batched_log, caller=log_batch[-1].caller))
