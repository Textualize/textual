from __future__ import annotations

from rich.console import RenderableType
from rich.panel import Panel

from textual import events
from textual.app import App, ComposeResult
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
        self.box = Box()
        yield self.box

    def key_a(self):
        self.animator.animate(
            self.box.styles,
            "opacity",
            value=0.0,
            duration=1.0,
            delay=5.0,
            on_complete=self.box.remove,
        )

    async def on_key(self, event: events.Key) -> None:
        await self.dispatch_key(event)


if __name__ == "__main__":
    app = JustABox(css_path="just_a_box.css", watch_css=True)
    app.run()
