from textual.app import App, ComposeResult
from textual.widgets import Button

TEXT = """I must not fear.
Fear is the mind-killer.
Fear is the little-death that brings total obliteration.
I will face my fear."""


class TooltipApp(App):
    CSS = """
    Screen {
        align: center middle;
    }
    Tooltip {
        padding: 2 4;
        background: $primary;
        color: auto 90%;
    }
    """

    def compose(self) -> ComposeResult:
        yield Button("Click me", variant="success")

    def on_mount(self) -> None:
        self.query_one(Button).tooltip = TEXT


if __name__ == "__main__":
    app = TooltipApp()
    app.run()
