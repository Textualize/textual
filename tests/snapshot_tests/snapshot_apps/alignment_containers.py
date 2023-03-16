"""
App to test alignment containers.
"""

from textual.app import App, ComposeResult
from textual.containers import Center, Middle
from textual.widgets import Button


class AlignContainersApp(App[None]):
    CSS = """
    Center {
        tint: $primary 10%;
    }
    Middle {
        tint: $secondary 10%;
    }
    """

    def compose(self) -> ComposeResult:
        with Center():
            yield Button.success("center")
        with Middle():
            yield Button.error("middle")


app = AlignContainersApp()
if __name__ == "__main__":
    app.run()
