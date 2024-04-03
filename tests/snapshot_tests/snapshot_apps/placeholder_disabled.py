from textual.app import App, ComposeResult
from textual.widgets import Placeholder

class DisabledPlaceholderApp(App[None]):

    CSS = """
    Placeholder {
        height: 1fr;
    }
    """

    def compose(self) -> ComposeResult:
        yield Placeholder()
        yield Placeholder(disabled=True)

if __name__ == "__main__":
    DisabledPlaceholderApp().run()

