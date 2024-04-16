from textual.app import App, ComposeResult
from textual.widgets import Button


class ButtonWithMultilineLabelApp(App):
    def compose(self) -> ComposeResult:
        yield Button("Button\nwith\nmulti-line\nlabel")


if __name__ == "__main__":
    app = ButtonWithMultilineLabelApp()
    app.run()
