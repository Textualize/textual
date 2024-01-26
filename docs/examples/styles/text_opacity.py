from textual.app import App
from textual.widgets import Label


class TextOpacityApp(App):
    CSS_PATH = "text_opacity.tcss"

    def compose(self):
        yield Label("text-opacity: 0%", id="zero-opacity")
        yield Label("text-opacity: 25%", id="quarter-opacity")
        yield Label("text-opacity: 50%", id="half-opacity")
        yield Label("text-opacity: 75%", id="three-quarter-opacity")
        yield Label("text-opacity: 100%", id="full-opacity")


if __name__ == "__main__":
    app = TextOpacityApp()
    app.run()
