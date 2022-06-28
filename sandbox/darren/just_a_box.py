from __future__ import annotations

from rich.console import RenderableType
from rich.panel import Panel

from textual.app import App, ComposeResult
from textual.widget import Widget


class Box(Widget):
    CSS = "#box {background: blue;}"

    def __init__(
        self, id: str | None = None, classes: str | None = None, *children: Widget
    ):
        super().__init__(*children, id=id, classes=classes)

    def render(self) -> RenderableType:
        return Panel("Box")


class JustABox(App):
    def compose(self) -> ComposeResult:
        yield Box(id="box")


if __name__ == "__main__":
    app = JustABox(css_path="just_a_box.css", watch_css=True)
    app.run()
