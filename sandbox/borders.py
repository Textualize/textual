from rich.console import RenderableType
from rich.text import Text

from textual.app import App, ComposeResult
from textual.css.types import EdgeType
from textual.widget import Widget
from textual.widgets import Placeholder


class VerticalContainer(Widget):
    DEFAULT_CSS = """
    VerticalContainer {
        layout: vertical;
        overflow: hidden auto;
        background: darkblue;
    }

    VerticalContainer Placeholder {
        margin: 1 0;
        height: auto;
        align: center top;
    }
    """


class Introduction(Widget):
    DEFAULT_CSS = """
    Introduction {
        background: indigo;
        color: white;
        height: 3;
        padding: 1 0;
    }
    """

    def render(self) -> RenderableType:
        return Text("Here are the color edge types we support.", justify="center")


class BorderDemo(Widget):
    def __init__(self, name: str):
        super().__init__(name=name)

    def render(self) -> RenderableType:
        return Text(self.name, style="black on yellow", justify="center")


class MyTestApp(App):
    def compose(self) -> ComposeResult:
        border_demo_widgets = []
        for border_edge_type in EdgeType.__args__:
            border_demo = BorderDemo(f'"border: {border_edge_type} white"')
            border_demo.styles.height = "auto"
            border_demo.styles.margin = (1, 0)
            border_demo.styles.border = (border_edge_type, "white")
            border_demo_widgets.append(border_demo)

        yield VerticalContainer(Introduction(), *border_demo_widgets, id="root")

    def on_mount(self):
        self.bind("q", "quit")


app = MyTestApp()

if __name__ == "__main__":
    app.run()
