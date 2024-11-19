from textual.app import App, ComposeResult
from textual.widgets import Button


class OnDecoratorApp(App):
    CSS_PATH = "on_decorator.tcss"

    def compose(self) -> ComposeResult:
        """Three buttons."""
        yield Button("Bell", id="bell")
        yield Button("Toggle dark", classes="toggle dark")
        yield Button("Quit", id="quit")

    def on_button_pressed(self, event: Button.Pressed) -> None:  # (1)!
        """Handle all button pressed events."""
        if event.button.id == "bell":
            self.bell()
        elif event.button.has_class("toggle", "dark"):
            self.theme = (
                "textual-dark" if self.theme == "textual-light" else "textual-light"
            )
        elif event.button.id == "quit":
            self.exit()


if __name__ == "__main__":
    app = OnDecoratorApp()
    app.run()
