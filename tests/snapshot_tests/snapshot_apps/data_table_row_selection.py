from textual.app import App, ComposeResult
from textual.widgets import DataTable

ROWS = [
    ("Name", "Role", "Status"),
    ("Ada", "Engineer", "Active"),
    ("Grace", "Admiral", "Active"),
    ("Katherine", "Mathematician", "Active"),
    ("Margaret", "Programmer", "Active"),
]


class TableApp(App):
    def compose(self) -> ComposeResult:
        table = DataTable(cursor_type="row")
        table.focus()
        yield table

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        rows = iter(ROWS)
        table.add_columns(*next(rows))
        row_keys = table.add_rows(rows)
        table.select_row(row_keys[0])
        table.select_row(row_keys[2])


if __name__ == "__main__":
    app = TableApp()
    app.run()
