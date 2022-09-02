from rich.console import RenderableType
from rich.text import Text

from textual.app import App, ComposeResult
from textual.widget import Widget
from textual.widgets import Placeholder

placeholders_count = 12


class VerticalContainer(Widget):
    DEFAULT_CSS = """
    VerticalContainer {
        layout: vertical;
        overflow: hidden auto;
        background: darkblue;
    }

    VerticalContainer Placeholder {
        margin: 1 0;
        height: 5;
        border: solid lime;
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
        return Text(
            "Press keys 0 to 9 to scroll to the Placeholder with that ID.",
            justify="center",
        )


class MyTestApp(App):
    def compose(self) -> ComposeResult:
        placeholders = [
            Placeholder(id=f"placeholder_{i}", name=f"Placeholder #{i}")
            for i in range(placeholders_count)
        ]

        yield VerticalContainer(Introduction(), *placeholders, id="root")

    def on_mount(self):
        self.bind("q", "quit")
        self.bind("t", "tree")
        for widget_index in range(placeholders_count):
            self.bind(str(widget_index), f"scroll_to('placeholder_{widget_index}')")

    def action_tree(self):
        self.log(self.tree)

    async def action_scroll_to(self, target_placeholder_id: str):
        target_placeholder = self.query(f"#{target_placeholder_id}").first()
        target_placeholder_container = self.query("#root").first()
        target_placeholder_container.scroll_to_widget(target_placeholder, animate=True)


app = MyTestApp()

if __name__ == "__main__":
    app.run()
