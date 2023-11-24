from textual.app import App, ComposeResult
from textual.containers import Grid
from textual.widgets import Placeholder


class KeylineApp(App):
    CSS_PATH = "keyline.tcss"

    def compose(self) -> ComposeResult:
        with Grid():
            yield Placeholder(id="foo")
            yield Placeholder(id="bar")
            yield Placeholder()
            yield Placeholder(classes="hidden")
            yield Placeholder(id="baz")


if __name__ == "__main__":
    KeylineApp().run()
