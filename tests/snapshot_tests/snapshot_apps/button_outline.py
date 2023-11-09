from textual.app import App, ComposeResult
from textual.widgets import Button


class ButtonIssue(App[None]):
    AUTO_FOCUS = None
    CSS = """
    Button {
        outline: white;
    }
    """

    def compose(self) -> ComposeResult:
        yield Button("Test")


if __name__ == "__main__":
    ButtonIssue().run()
