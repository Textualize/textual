from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Static


class HorizontalAutoWidth(App):
    """
    Checks that the auto width of the parent Horizontal is correct.
    """

    def compose(self) -> ComposeResult:
        yield Horizontal(
            Static("Docked left 1", id="dock-1"),
            Static("Docked left 2", id="dock-2"),
            Static("Widget 1", classes="widget"),
            Static("Widget 2", classes="widget"),
            id="horizontal",
        )


app = HorizontalAutoWidth(css_path="horizontal_auto_width.tcss")
if __name__ == "__main__":
    app.run()
