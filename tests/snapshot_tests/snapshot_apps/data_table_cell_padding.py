from textual.app import App, ComposeResult
from textual.widgets import DataTable


class TableApp(App):
    CSS = """
    DataTable {
        margin: 1;
    }
    """

    def compose(self) -> ComposeResult:
        for cell_padding in range(5):
            dt = DataTable(cell_padding=cell_padding)
            dt.add_columns("one", "two", "three")
            dt.add_row("value", "value", "val")
            yield dt

    def key_a(self):
        self.query(DataTable).last().cell_padding = 20

    def key_b(self):
        self.query(DataTable).last().cell_padding = 10


app = TableApp()
if __name__ == "__main__":
    app.run()
