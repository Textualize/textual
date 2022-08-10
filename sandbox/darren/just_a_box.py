from __future__ import annotations

from rich.console import RenderableType
from rich.panel import Panel

from textual import events
from textual.app import App, ComposeResult
from textual.layout import Horizontal, Vertical
from textual.widget import Widget


class Box(Widget, can_focus=True):
    CSS = "#box {background: blue;}"

    def __init__(
        self, id: str | None = None, classes: str | None = None, *children: Widget
    ):
        super().__init__(*children, id=id, classes=classes)

    def render(self) -> RenderableType:
        return Panel("Box")


class JustABox(App):
    def compose(self) -> ComposeResult:
        yield Horizontal(
            Box(id="middle_pane"),
            Vertical(
                Box(id="box1", classes="box"),
                Box(id="box2", classes="box"),
                # Box(id="box3", classes="box"),
                # Box(id="box4", classes="box"),
                # Box(id="box5", classes="box"),
                # Box(id="box6", classes="box"),
                # Box(id="box7", classes="box"),
                # Box(id="box8", classes="box"),
                # Box(id="box9", classes="box"),
                # Box(id="box10", classes="box"),
                id="left_pane",
            ),
            Vertical(
                Box(id="boxa", classes="box"),
                Box(id="boxb", classes="box"),
                Box(id="boxc", classes="box"),
                id="right_pane",
            ),
            id="horizontal",
        )

    def key_p(self):
        print(self.query("#horizontal").first().styles.layout)

    async def on_key(self, event: events.Key) -> None:
        await self.dispatch_key(event)


if __name__ == "__main__":
    app = JustABox(css_path="just_a_box.css", watch_css=True)
    app.run()
