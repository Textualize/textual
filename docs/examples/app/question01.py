from textual.app import App, ComposeResult
from textual.widgets import Static, Button


class QuestionApp(App[str]):
    def compose(self) -> ComposeResult:
        yield Static("Do you love Textual?")
        yield Button("Yes", id="yes", variant="primary")
        yield Button("No", id="no", variant="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.exit(event.button.id)


app = QuestionApp()
if __name__ == "__main__":
    reply = app.run()
    print(reply)
