from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import TabbedContent, DataTable


class Dashboard(App):
    """Dashboard"""

    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        Binding("ctrl+q", "app.quit", "Quit", show=True),
    ]
    TITLE = "Dashboard"
    CSS = """

    DataTable {
        height: auto;
    }
    """

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        with TabbedContent("Workflows"):
            yield DataTable(id="table")

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("Id", "Description", "Status", "Result Id")
        for row in [(1, 2, 3, 4), ("a", "b", "c", "d"), ("fee", "fy", "fo", "fum")]:
            table.add_row(key=row[0], *row)


if __name__ == "__main__":
    app = Dashboard()
    app.run()
