from textual.app import App, ComposeResult
from textual.widgets import Button, Dialog, Label


class DialogApp(App[None]):
    CSS_PATH = "dialog.tcss"

    def compose(self) -> ComposeResult:
        with Dialog(title="Greetings Professor Falken"):
            yield Label("Shall we play a game?")
            with Dialog.ActionArea():
                yield Button("Love to!")
                yield Button("No thanks")


if __name__ == "__main__":
    DialogApp().run()
