from rich.console import RenderableType
from rich.text import Text

from textual.app import App, ComposeResult
from textual.widget import Widget
from textual.widgets import Placeholder

root_container_style = "border: solid white;"
initial_placeholders_count = 4


class VerticalContainer(Widget):
    CSS = """
    VerticalContainer {
        layout: vertical;
        overflow: hidden auto;
        background: darkblue;
        ${root_container_style}
    }

    VerticalContainer Placeholder {
        margin: 1 0;
        height: 5;
        border: solid lime;
        align: center top;
    }
    """.replace(
        "${root_container_style}", root_container_style
    )


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
        return Text(
            "Press '-' and '+' to add or remove placeholders.", justify="center"
        )


class MyTestApp(App):
    def compose(self) -> ComposeResult:
        # yield Introduction()

        placeholders = [
            Placeholder(id=f"placeholder_{i}", name=f"Placeholder #{i}")
            for i in range(initial_placeholders_count)
        ]

        yield VerticalContainer(Introduction(), *placeholders, id="root")

    def on_mount(self):
        self.bind("q", "quit")
        self.bind("t", "tree")
        self.bind("-", "remove_placeholder")
        self.bind("+", "add_placeholder")

    def action_tree(self):
        self.log(self.tree)

    async def action_remove_placeholder(self):
        placeholders = self.query("Placeholder")
        placeholders_count = len(placeholders)
        for i, placeholder in enumerate(placeholders):
            if i == placeholders_count - 1:
                await self.remove(placeholder)
                placeholder.parent.children._nodes.remove(placeholder)
        self.refresh(repaint=True, layout=True)
        self.refresh_css()

    async def action_add_placeholder(self):
        placeholders = self.query("Placeholder")
        placeholders_count = len(placeholders)
        placeholder = Placeholder(
            id=f"placeholder_{placeholders_count}",
            name=f"Placeholder #{placeholders_count}",
        )
        root = self.get_child("root")
        root.mount(placeholder)
        self.refresh(repaint=True, layout=True)
        self.refresh_css()


app = MyTestApp()

if __name__ == "__main__":
    app.run()
