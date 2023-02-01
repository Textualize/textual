from textual.app import App, ComposeResult
from textual.widgets import Button, Header, Label


class MyApp(App[str]):
    TITLE = "A Question App"
    SUB_TITLE = "The most important question"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("Do you love Textual?")
        yield Button("Yes", id="yes", variant="primary")
        yield Button("No", id="no", variant="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.exit(event.button.id)


if __name__ == "__main__":
    app = MyApp()
    reply = app.run()
    print(reply)
