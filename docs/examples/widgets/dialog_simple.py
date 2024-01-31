from textual.app import App, ComposeResult
from textual.widgets import Button, Dialog, Label


class DialogApp(App[None]):
    CSS_PATH = "dialog_simple.tcss"

    def compose(self) -> ComposeResult:
        with Dialog(title="Greetings Professor Falken"):  # (1)!
            yield Label("Shall we play a game?")  # (2)!
            with Dialog.ActionArea():  # (3)!
                yield Button("Love to!")  # (4)!
                yield Button("No thanks")  # (5)!


if __name__ == "__main__":
    DialogApp().run()
