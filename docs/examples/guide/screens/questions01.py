from textual import on, work
from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Label


class QuestionScreen(Screen):
    """Screen with a parameter."""

    def __init__(self, question: str) -> None:
        self.question = question
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Label(self.question)
        yield Button("Yes", id="yes", variant="success")
        yield Button("No", id="no")

    @on(Button.Pressed, "#yes")
    def handle_yes(self) -> None:
        self.dismiss(True)

    @on(Button.Pressed, "#no")
    def handle_no(self) -> None:
        self.dismiss(False)


class QuestionsApp(App):
    CSS_PATH = "questions01.tcss"

    @work
    async def on_mount(self) -> None:
        if await self.push_screen(
            QuestionScreen("Do you like Textual?"), wait_for_dismiss=True
        ):
            self.notify("Good answer!")
        else:
            self.notify(":-(", severity="error")


if __name__ == "__main__":
    app = QuestionsApp()
    app.run()
