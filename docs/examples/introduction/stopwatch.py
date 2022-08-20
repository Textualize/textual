from time import monotonic

from textual.app import App, ComposeResult
from textual.layout import Container
from textual.reactive import Reactive
from textual.widgets import Button, Header, Footer, Static


class TimeDisplay(Static):
    """Displays the time."""

    time = Reactive(0.0)

    def watch_time(self, time: float) -> None:
        """Called when time_delta changes."""
        minutes, seconds = divmod(time, 60)
        hours, minutes = divmod(minutes, 60)
        self.update(f"{hours:02.0f}:{minutes:02.0f}:{seconds:05.2f}")


class Stopwatch(Static):
    """The timer widget (display + buttons)."""

    start_time = Reactive(0.0)
    total = Reactive(0.0)
    started = Reactive(False)

    def watch_started(self, started: bool) -> None:
        """Called when the 'started' attribute changes."""
        if started:
            self.start_time = monotonic()
            self.update_timer.resume()
            self.add_class("started")
            self.query_one("#stop").focus()
        else:
            self.update_timer.pause()
            self.total += monotonic() - self.start_time
            self.remove_class("started")
            self.query_one("#start").focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Called when a button is pressed."""
        button_id = event.button.id
        self.started = button_id == "start"
        if button_id == "reset":
            self.total = 0.0
            self.update_elapsed()

    def on_mount(self) -> None:
        """Called when widget is first added."""
        self.update_timer = self.set_interval(1 / 30, self.update_elapsed, pause=True)

    def update_elapsed(self) -> None:
        """Updates elapsed time."""
        self.query_one(TimeDisplay).time = (
            self.total + monotonic() - self.start_time if self.started else self.total
        )

    def compose(self) -> ComposeResult:
        """Composes the timer widget."""
        yield Button("Start", id="start", variant="success")
        yield Button("Stop", id="stop", variant="error")
        yield Button("Reset", id="reset")
        yield TimeDisplay()


class StopwatchApp(App):
    """Manage the timers."""

    def on_load(self) -> None:
        """Called when the app first loads."""
        self.bind("a", "add_timer", description="Add")
        self.bind("r", "remove_timer", description="Remove")
        self.bind("d", "toggle_dark", description="Dark mode")

    def compose(self) -> ComposeResult:
        """Called to ad widgets to the app."""
        yield Header()
        yield Footer()
        yield Container(Stopwatch(), Stopwatch(), Stopwatch(), id="timers")

    def action_add_timer(self) -> None:
        """An action to add a timer."""
        new_timer = Stopwatch()
        self.query_one("#timers").mount(new_timer)
        new_timer.scroll_visible()

    def action_remove_timer(self) -> None:
        """Called to remove a timer."""
        timers = self.query("#timers Stopwatch")
        if timers:
            timers.last().remove()

    def action_toggle_dark(self) -> None:
        self.dark = not self.dark


app = StopwatchApp(css_path="stopwatch.css")
if __name__ == "__main__":
    app.run()
