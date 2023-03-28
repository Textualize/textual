from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Header, Footer, Label
from textual.binding import Binding


class Dialog(Vertical):
    def compose(self) -> ComposeResult:
        """Compose the child widgets."""
        yield Label("This should not cause a scrollbar to appear")


class DialogIssueApp(App[None]):
    CSS = """
    Screen {
        layers: base dialog;
    }

    .hidden {
        display: none;
    }

    Dialog {
        align: center middle;
        border: round red;
        width: 50%;
        height: 50%;
        layer: dialog;
        offset: 50% 50%;
    }
    """

    BINDINGS = [
        Binding("d", "dialog", "Toggle the dialog"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Vertical()
        yield Dialog(classes="hidden")
        yield Footer()

    def action_dialog(self) -> None:
        self.query_one(Dialog).toggle_class("hidden")


if __name__ == "__main__":
    DialogIssueApp().run()
