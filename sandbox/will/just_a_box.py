from __future__ import annotations

from rich.console import RenderableType
from rich.panel import Panel

from textual import events
from textual.app import App, ComposeResult
from textual.layout import Container, Horizontal, Vertical
from textual.widget import Widget


class Box(Widget, can_focus=True):
    DEFAULT_CSS = "#box {background: blue;}"

    def render(self) -> RenderableType:
        return Panel("Box")


class JustABox(App):
    def compose(self) -> ComposeResult:
        # yield Container(Box(classes="box"))
        yield Horizontal(
            Vertical(
                Box(id="box1", classes="box"),
                Box(id="box2", classes="box"),
                id="left_pane",
            ),
            id="horizontal",
        )

    def key_p(self):
        for k, v in self.app.stylesheet.source.items():
            print(k)
        print(self.query_one("#horizontal").styles.layout)

    async def on_key(self, event: events.Key) -> None:
        await self.dispatch_key(event)


app = JustABox(css_path="just_a_box.css", watch_css=True)

if __name__ == "__main__":
    app.run()
