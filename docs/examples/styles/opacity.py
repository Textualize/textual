from textual.app import App
from textual.widgets import Label


class OpacityApp(App):
    CSS_PATH = "opacity.tcss"

    def compose(self):
        yield Label("opacity: 0%", id="zero-opacity")
        yield Label("opacity: 25%", id="quarter-opacity")
        yield Label("opacity: 50%", id="half-opacity")
        yield Label("opacity: 75%", id="three-quarter-opacity")
        yield Label("opacity: 100%", id="full-opacity")


if __name__ == "__main__":
    app = OpacityApp()
    app.run()
