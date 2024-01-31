from textual.app import App, ComposeResult
from textual.widgets import Button, Dialog, Label


class SuccessDialogApp(App[None]):
    CSS_PATH = "dialog_variants.tcss"

    def compose(self) -> ComposeResult:
        with Dialog.success(title="Search Successful"):
            yield Label("Admiral. We have found the nuclear wessel.")
            with Dialog.ActionArea():
                yield Button("OK")


if __name__ == "__main__":
    SuccessDialogApp().run()
