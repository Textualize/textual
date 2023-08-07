from threading import Thread

import pytest

from textual.app import App, ComposeResult
from textual.widgets import RichLog


def test_call_from_thread_app_not_running():
    app = App()

    # Should fail if app is not running
    with pytest.raises(RuntimeError):
        app.call_from_thread(print)


def test_call_from_thread():
    """Test the call_from_thread method."""

    class BackgroundThread(Thread):
        """A background thread which will modify app in some way."""

        def __init__(self, app: App[object]) -> None:
            self.app = app
            super().__init__()

        def run(self) -> None:
            def write_stuff(text: str) -> None:
                """Write stuff to a widget."""
                self.app.query_one(RichLog).write(text)

            self.app.call_from_thread(write_stuff, "Hello")
            # Exit the app with a code we can assert
            self.app.call_from_thread(self.app.exit, 123)

    class ThreadTestApp(App[object]):
        """Trivial app with a single widget."""

        def compose(self) -> ComposeResult:
            yield RichLog()

        def on_ready(self) -> None:
            """Launch a thread which will modify the app."""
            try:
                self.call_from_thread(print)
            except RuntimeError as error:
                # Calling this from the same thread as the app is an error
                self._runtime_error = error
            BackgroundThread(self).start()

    app = ThreadTestApp()
    result = app.run(headless=True, size=(80, 24))
    assert isinstance(app._runtime_error, RuntimeError)
    assert result == 123
