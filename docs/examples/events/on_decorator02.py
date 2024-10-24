from textual import on
from textual.app import App, ComposeResult
from textual.widgets import Button


class OnDecoratorApp(App):
    CSS_PATH = "on_decorator.tcss"

    def compose(self) -> ComposeResult:
        """Three buttons."""
        yield Button("Bell", id="bell")
        yield Button("Toggle dark", classes="toggle dark")
        yield Button("Quit", id="quit")

    @on(Button.Pressed, "#bell")  # (1)!
    def play_bell(self):
        """Called when the bell button is pressed."""
        self.bell()

    @on(Button.Pressed, ".toggle.dark")  # (2)!
    def toggle_dark(self):
        """Called when the 'toggle dark' button is pressed."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    @on(Button.Pressed, "#quit")  # (3)!
    def quit(self):
        """Called when the quit button is pressed."""
        self.exit()


if __name__ == "__main__":
    app = OnDecoratorApp()
    app.run()
