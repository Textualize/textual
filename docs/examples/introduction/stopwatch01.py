from textual.app import App
from textual.widgets import Header, Footer


class StopwatchApp(App):
    def compose(self):
        yield Header()
        yield Footer()

    def on_load(self):
        self.bind("d", "toggle_dark", description="Dark mode")

    def action_toggle_dark(self):
        self.dark = not self.dark


app = StopwatchApp()
if __name__ == "__main__":
    app.run()
