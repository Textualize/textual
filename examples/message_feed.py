"""
Async message feed — a real-time log viewer that polls a queue in the background.

Demonstrates:
- `work` decorator for background async tasks
- `RichLog` for live-appending output
- `call_from_thread` for thread-safe UI updates
- Keyboard bindings to pause/resume and clear the feed
"""

import asyncio
from datetime import datetime

from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.widgets import Footer, Header, RichLog, Static


class MessageFeedApp(App):
    """Live async message feed with pause/resume and clear."""

    TITLE = "Message Feed"
    CSS = """
    Screen { layers: base; }
    #status { height: 1; background: $panel; padding: 0 1; }
    #feed   { border: solid $primary; height: 1fr; }
    """

    BINDINGS = [
        Binding("p", "toggle_pause", "Pause/Resume"),
        Binding("c", "clear", "Clear"),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(self):
        super().__init__()
        self._queue: asyncio.Queue[str] = asyncio.Queue()
        self._paused = False

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical():
            yield Static("▶ running", id="status")
            yield RichLog(id="feed", highlight=True, markup=True)
        yield Footer()

    def on_mount(self) -> None:
        self._produce()
        self._consume()

    @work(exclusive=True)
    async def _produce(self) -> None:
        """Simulate an async message source (replace with your real source)."""
        counter = 0
        while True:
            await asyncio.sleep(0.8)
            counter += 1
            ts = datetime.now().strftime("%H:%M:%S")
            await self._queue.put(f"[dim]{ts}[/] message [bold]{counter}[/]")

    @work(exclusive=True)
    async def _consume(self) -> None:
        """Drain the queue and append to the feed."""
        feed = self.query_one("#feed", RichLog)
        while True:
            msg = await self._queue.get()
            if not self._paused:
                feed.write(msg)

    def action_toggle_pause(self) -> None:
        self._paused = not self._paused
        status = self.query_one("#status", Static)
        if self._paused:
            status.update("⏸ paused")
        else:
            status.update("▶ running")

    def action_clear(self) -> None:
        self.query_one("#feed", RichLog).clear()


if __name__ == "__main__":
    MessageFeedApp().run()
