from rich.console import RenderableType
from rich.text import Text

from textual.app import App, ComposeResult
from textual.css.types import EdgeType
from textual.widget import Widget
from textual.widgets import Placeholder


class VerticalContainer(Widget):
    CSS = """
    VerticalContainer {
        layout: vertical;
        overflow: hidden auto;
        background: darkblue;
    }

    VerticalContainer Placeholder {
        margin: 1 0;
        height: 5;
        align: center top;
    }
    """


class Introduction(Widget):
    CSS = """
    Introduction {
        background: indigo;
        color: white;
        height: 3;
        padding: 1 0;
    }
    """

    def render(self, styles) -> RenderableType:
        return Text("Here are the color edge types we support.", justify="center")


class MyTestApp(App):
    def compose(self) -> ComposeResult:
        placeholders = []
        for border_edge_type in EdgeType.__args__:
            border_placeholder = Placeholder(
                id=f"placeholder_{border_edge_type}",
                title=(border_edge_type or " ").upper(),
                name=f"border: {border_edge_type} white",
            )
            border_placeholder.styles.border = (border_edge_type, "white")
            placeholders.append(border_placeholder)

        yield VerticalContainer(Introduction(), *placeholders, id="root")

    def on_mount(self):
        self.bind("q", "quit")
        self.bind("t", "tree")

    def action_tree(self):
        self.log(self.tree)


app = MyTestApp()

if __name__ == "__main__":
    app.run()
