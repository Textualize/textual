from __future__ import annotations

import inspect
from typing import NamedTuple, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from textual.app import App


class DevtoolsLog(NamedTuple):
    objects_or_string: tuple[Any, ...] | str
    caller: inspect.FrameInfo | None = None


class DevtoolsWritable:
    def __init__(self, app: App):
        self.app = app
        self._buffer: list[DevtoolsLog] = []

    def write(self, string: str) -> None:
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

    def flush(self):
        log_batch: list[DevtoolsLog] = []
        for log in self._buffer:
            end_of_batch = (
                log_batch and log_batch[-1].caller.filename != log.caller.filename
            )
            if end_of_batch:
                self._log_batched(log_batch)
                log_batch.clear()
            log_batch.append(log)

        if log_batch:
            self._log_batched(log_batch)

        self._buffer.clear()

    def _log_batched(self, log_batch: list[DevtoolsLog]) -> None:
        batched_log = "".join(log.objects_or_string for log in log_batch)
        batched_log = batched_log.rstrip()
        if self.app.devtools.is_connected:
            self.app.devtools.log(DevtoolsLog(batched_log, caller=log_batch[-1].caller))
