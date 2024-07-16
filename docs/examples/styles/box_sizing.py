from textual.app import App
from textual.widgets import Static


class BoxSizingApp(App):
    CSS_PATH = "box_sizing.tcss"

    def compose(self):
        yield Static("I'm using border-box!", id="static1")
        yield Static("I'm using content-box!", id="static2")


if __name__ == "__main__":
    app = BoxSizingApp()
    app.run()
