from textual.app import App, ComposeResult
from textual.widgets import Button, Label


class QuestionApp(App[str]):
    CSS_PATH = "question02.tcss"

    def compose(self) -> ComposeResult:
        yield Label("Do you love Textual?", id="question")
        yield Button("Yes", id="yes", variant="primary")
        yield Button("No", id="no", variant="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.exit(event.button.id)


if __name__ == "__main__":
    app = QuestionApp()
    reply = app.run()
    print(reply)
