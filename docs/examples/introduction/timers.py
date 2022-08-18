from time import time

from textual.app import App, ComposeResult
from textual.layout import Container
from textual.reactive import Reactive
from textual.widgets import Button, Header, Footer, Static


class TimeDisplay(Static):
    """Displays the time."""

    time_delta = Reactive(0.0)

    def watch_time_delta(self, time_delta: float) -> None:
        minutes, seconds = divmod(time_delta, 60)
        hours, minutes = divmod(minutes, 60)
        self.update(f"{hours:02.0f}:{minutes:02.0f}:{seconds:02.2f}")


class TimerWidget(Static):
    """The timer widget (display + buttons)."""

    start_time = Reactive(0.0)
    total = Reactive(0.0)
    started = Reactive(False)

    def on_mount(self) -> None:
        self.update_timer = self.set_interval(1 / 30, self.update_elapsed, pause=True)

    def update_elapsed(self) -> None:
        time_delta = (
            self.total + time() - self.start_time if self.started else self.total
        )
        self.query_one(TimeDisplay).time_delta = time_delta

    def compose(self) -> ComposeResult:
        yield Button("Start", id="start", variant="success")
        yield Button("Stop", id="stop", variant="error")
        yield TimeDisplay()
        yield Button("Reset", id="reset")

    def watch_started(self, started: bool) -> None:
        if started:
            self.start_time = time()
            self.update_timer.resume()
            self.add_class("started")
        else:
            self.update_timer.pause()
            self.total += time() - self.start_time
            self.remove_class("started")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        self.started = button_id == "start"
        if button_id == "reset":
            self.started = False
            self.total = 0.0
            self.update_elapsed()


class TimerApp(App):
    def on_load(self) -> None:
        self.bind("a", "add_timer", description="Add")
        self.bind("r", "remove_timer", description="Remove")

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield Container(TimerWidget(), TimerWidget(), TimerWidget())

    def action_add_timer(self) -> None:
        new_timer = TimerWidget()
        self.query_one("Container").mount(new_timer)
        self.call_later(new_timer.scroll_visible)

    def action_remove_timer(self) -> None:
        timers = self.query("Container TimerWidget")
        if timers:
            timers.last().remove()


app = TimerApp(css_path="timers.css")
if __name__ == "__main__":
    app.run()
