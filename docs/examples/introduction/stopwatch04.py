from textual.app import App, ComposeResult
from textual.layout import Container
from textual.reactive import Reactive
from textual.widgets import Button, Header, Footer, Static


class TimeDisplay(Static):
    pass


class Stopwatch(Static):
    started = Reactive(False)

    def watch_started(self, started: bool) -> None:
        if started:
            self.add_class("started")
        else:
            self.remove_class("started")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Called when a button is pressed."""
        button_id = event.button.id
        self.started = button_id == "start"

    def compose(self) -> ComposeResult:
        yield Button("Start", id="start", variant="success")
        yield Button("Stop", id="stop", variant="error")
        yield Button("Reset", id="reset")
        yield TimeDisplay("00:00:00.00")


class StopwatchApp(App):
    def compose(self):
        yield Header()
        yield Footer()
        yield Container(Stopwatch(), Stopwatch(), Stopwatch())

    def on_load(self):
        self.bind("d", "toggle_dark", description="Dark mode")

    def action_toggle_dark(self):
        self.dark = not self.dark


app = StopwatchApp(css_path="stopwatch04.css")
if __name__ == "__main__":
    app.run()
