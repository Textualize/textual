from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Static


CSS_PATH = (Path(__file__) / "../hot_reloading_text_style.css").resolve()

# Write some CSS to the file before the app loads.
# Then, the test will clear all the CSS to see if the
# hot reloading applies the changes correctly.
CSS_PATH.write_text(
    """
Container {
    align: center middle;
    width: 100%;
}

#hello {
    text-align: left;
}
"""
)


class HotReloadingApp(App[None]):
    CSS_PATH = CSS_PATH

    def compose(self) -> ComposeResult:
        yield Container(Static("Should be right aligned", id="hello"))
