from rich.console import RenderableType

from textual import layout
from textual.app import App, ComposeResult
from textual.widgets import Static


class Box(Static):
    def render(self) -> RenderableType:
        x, y = self.styles.offset
        return f"{self.id}: offset = ({x}, {y})"


class OffsetExample(App):
    def compose(self) -> ComposeResult:
        yield layout.Container(
            Box(id="box1"),
            Box(id="box2"),
            Box(id="box3"),
            Box(id="box4"),
            id="parent",
        )


app = OffsetExample(css_path="offset.css")
if __name__ == "__main__":
    app.run()
