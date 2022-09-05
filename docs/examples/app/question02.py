from textual.app import App, ComposeResult
from textual.widgets import Static, Button


class QuestionApp(App[str]):
    def compose(self) -> ComposeResult:
        yield Static("Do you love Textual?")
        yield (yes := Button("Yes", id="yes"))
        yes.variant = "primary"
        yield (no := Button("No", id="no"))
        no.variant = "error"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.exit(event.button.id)


app = QuestionApp()
if __name__ == "__main__":
    reply = app.run()
    print(reply)
