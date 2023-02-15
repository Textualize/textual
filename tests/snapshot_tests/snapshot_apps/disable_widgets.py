from textual.app import App, ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import (
    Header,
    Footer,
    Button,
    DataTable,
    Input,
    ListView,
    ListItem,
    Label,
    Markdown,
    MarkdownViewer,
    Tree,
    TextLog,
)


class WidgetDisableTestApp(App[None]):

    CSS = """
    Horizontal {
        height: auto;
    }
    DataTable, ListView, Tree, TextLog {
        height: 2;
    }

    Markdown, MarkdownViewer {
        height: 1fr;
    }
    """

    @property
    def data_table(self) -> DataTable:
        data_table = DataTable[str]()
        data_table.add_columns("Column 1", "Column 2", "Column 3", "Column 4")
        data_table.add_rows(
            [(str(n), str(n * 10), str(n * 100), str(n * 1000)) for n in range(100)]
        )
        return data_table

    @property
    def list_view(self) -> ListView:
        return ListView(*[ListItem(Label(f"This is list item {n}")) for n in range(20)])

    @property
    def test_tree(self) -> Tree:
        tree = Tree[None](label="This is a test tree")
        for n in range(10):
            tree.root.add_leaf(f"Leaf {n}")
        tree.root.expand()
        return tree

    def compose(self) -> ComposeResult:
        yield Header()
        yield Vertical(
            Horizontal(
                Button(),
                Button(variant="primary"),
                Button(variant="success"),
                Button(variant="warning"),
                Button(variant="error"),
            ),
            self.data_table,
            self.list_view,
            self.test_tree,
            TextLog(),
            Input(),
            Input(placeholder="This is an empty input with a placeholder"),
            Input("This is some text in an input"),
            Markdown("# Hello, World!"),
            MarkdownViewer("# Hello, World!"),
            id="test-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        self.query_one(TextLog).write("Hello, World!")
        self.query_one("#test-container", Vertical).disabled = True


if __name__ == "__main__":
    WidgetDisableTestApp().run()
