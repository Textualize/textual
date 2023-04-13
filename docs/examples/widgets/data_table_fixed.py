from textual.app import App, ComposeResult
from textual.widgets import DataTable


class TableApp(App):
    CSS = "DataTable {height: 1fr}"

    def compose(self) -> ComposeResult:
        yield DataTable()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.focus()
        table.add_columns("A", "B", "C")
        for number in range(1, 100):
            table.add_row(str(number), str(number * 2), str(number * 3))
        table.fixed_rows = 2
        table.fixed_columns = 1
        table.cursor_type = "row"
        table.zebra_stripes = True


app = TableApp()
if __name__ == "__main__":
    app.run()
