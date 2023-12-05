from textual.app import App, ComposeResult
from textual.widgets import DataTable, Static


class HappyDataTableFunApp(App[None]):
    """The DataTable should expand as if it has height 1fr."""

    CSS = """
    DataTable {
        max-height: 100%;        
    }
    """

    def populate(self, table: DataTable) -> DataTable:
        for n in range(20):
            table.add_column(f"Column {n}")
        for row in range(100):
            table.add_row(*[str(row * n) for n in range(20)])
        return table

    def compose(self) -> ComposeResult:
        with Static(id="s"):
            yield self.populate(DataTable())


if __name__ == "__main__":
    HappyDataTableFunApp().run()
