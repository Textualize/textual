from textual import on
from textual.app import App, ComposeResult
from textual.widgets import Button


class OnDecoratorApp(App):
    CSS_PATH = "on_decorator.css"

    def compose(self) -> ComposeResult:
        """Three buttons."""
        yield Button("Bell", id="bell")
        yield Button("Toggle dark", classes="toggle dark")
        yield Button("Quit", id="quit")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle all button pressed events."""
        if event.button.id == "bell":
            self.app.bell()
        elif event.button.has_class("toggle", "dark"):
            self.app.dark = not self.app.dark
        elif event.button.id == "quit":
            self.app.exit()


if __name__ == "__main__":
    app = OnDecoratorApp()
    app.run()
