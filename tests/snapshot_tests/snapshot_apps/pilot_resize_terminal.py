from textual.app import App, ComposeResult
from textual.widgets import Label


class SingleLabelApp(App[None]):
    """An app with a single label that's 20 x 10."""

    def compose(self) -> ComposeResult:
        yield Label(("12345678901234567890\n" * 10).strip())


if __name__ == "__main__":
    SingleLabelApp().run()
