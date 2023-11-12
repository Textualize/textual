from textual.app import App, ComposeResult
from textual.widgets import Button


class ButtonApp(App):
    CSS = """
    Button {
        height: 9;
    }
    """

    def compose(self) -> ComposeResult:
        yield Button("Hello")
        yield Button("Hello\nWorld !!")


if __name__ == "__main__":
    app = ButtonApp()
    app.run()
