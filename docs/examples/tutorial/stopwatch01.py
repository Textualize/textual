from textual.app import App, ComposeResult
from textual.widgets import Header, Footer


class StopwatchApp(App):
    """A Textual app to manage stopwatches."""

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()

    def on_load(self) -> None:
        """Called when app first loads."""
        self.bind("d", "toggle_dark", description="Dark mode")

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark


app = StopwatchApp()
if __name__ == "__main__":
    app.run()
