from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Label


SCREEN_CSS_PATH = (Path(__file__) / "../hot_reloading_app_with_screen_css.tcss").resolve()

# Write some CSS to the file before the app loads.
# Then, the test will clear all the CSS to see if the
# hot reloading applies the changes correctly.
SCREEN_CSS_PATH.write_text(
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


class MyScreen(Screen[None]):
    CSS_PATH = SCREEN_CSS_PATH

    def compose(self) -> ComposeResult:
        yield Container(Label("Hello, world!"))


class HotReloadingApp(App[None]):
    def on_mount(self) -> None:
        self.push_screen(MyScreen())


if __name__ == "__main__":
    HotReloadingApp(watch_css=True).run()
