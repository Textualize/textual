from textual.app import App
from textual.widgets import Static


class DisplayApp(App):
    CSS_PATH = "display.tcss"

    def compose(self):
        yield Static("Widget 1")
        yield Static("Widget 2", classes="remove")
        yield Static("Widget 3")


if __name__ == "__main__":
    app = DisplayApp()
    app.run()
