from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Label


class SuspendKeysApp(App[None]):

    BINDINGS = [Binding("ctrl+z", "suspend_process")]

    def compose(self) -> ComposeResult:
        yield Label("Press Ctrl+Z to suspend!")


if __name__ == "__main__":
    SuspendKeysApp().run()
