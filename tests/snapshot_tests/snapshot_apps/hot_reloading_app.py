from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Label


CSS_PATH = (Path(__file__) / "../hot_reloading_app.tcss").resolve()

# Write some CSS to the file before the app loads.
# Then, the test will clear all the CSS to see if the
# hot reloading applies the changes correctly.
CSS_PATH.write_text(
    """
Container {
    align: center middle;
}

Label {
    border: round $primary;
    padding: 3;
}
"""
)


class HotReloadingApp(App[None]):
    CSS_PATH = CSS_PATH

    def compose(self) -> ComposeResult:
        yield Container(Label("Hello, world!"))
