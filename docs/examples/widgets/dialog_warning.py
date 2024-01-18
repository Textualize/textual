from textual.app import App, ComposeResult
from textual.widgets import Button, Dialog, Label


class WarningDialogApp(App[None]):
    CSS_PATH = "dialog_variants.tcss"

    def compose(self) -> ComposeResult:
        with Dialog.warning(title="Are you sure?"):
            yield Label(
                "Admiral, if we were to assume these whales were ours to do with as we pleased, "
                "we would be as guilty as those who caused their extinction."
            )
            with Dialog.ActionArea():
                yield Button("OK")
                yield Button("Cancel")


if __name__ == "__main__":
    WarningDialogApp().run()
