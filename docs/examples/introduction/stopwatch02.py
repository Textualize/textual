from textual.app import App
from textual.layout import Container
from textual.widgets import Button, Header, Footer, Static


class TimeDisplay(Static):
    pass


class Stopwatch(Static):
    def compose(self):
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


app = StopwatchApp()
if __name__ == "__main__":
    app.run()
