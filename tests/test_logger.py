import inspect
from typing import Any

from textual import work
from textual._log import LogGroup, LogVerbosity
from textual.app import App


async def test_log_from_worker() -> None:
    """Check that log calls from threaded workers call app._log"""

    log_messages: list[tuple] = []

    class LogApp(App):

        def _log(
            self,
            group: LogGroup,
            verbosity: LogVerbosity,
            _textual_calling_frame: inspect.Traceback,
            *objects: Any,
            **kwargs,
        ) -> None:
            log_messages.append(objects)

        @property
        def _is_devtools_connected(self):
            """Fake connected devtools."""
            return True

        def on_mount(self) -> None:
            self.do_work()
            self.call_after_refresh(self.exit)

        @work(thread=True)
        def do_work(self) -> None:
            self.log("HELLO from do_work")

    app = LogApp()
    async with app.run_test() as pilot:
        await pilot.pause()
        assert ("HELLO from do_work",) in log_messages
