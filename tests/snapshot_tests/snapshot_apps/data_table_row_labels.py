from textual.app import App, ComposeResult
from textual.widgets import DataTable

ROWS = [
    ("lane", "swimmer", "country", "time"),
    (5, "Chad le Clos", "South Africa", 51.14),
    (4, "Joseph Schooling", "Singapore", 50.39),
    (2, "Michael Phelps", "United States", 51.14),
    (6, "László Cseh", "Hungary", 51.14),
    (3, "Li Zhuhao", "China", 51.26),
    (8, "Mehdy Metella", "France", 51.58),
    (7, "Tom Shields", "United States", 51.73),
    (10, "Darren Burns", "Scotland", 51.84),
    (1, "Aleksandr Sadovnikov", "Russia", 51.84),
]


class TableApp(App):
    def compose(self) -> ComposeResult:
        yield DataTable()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.fixed_rows = 1
        table.fixed_columns = 1
        table.focus()
        rows = iter(ROWS)
        column_labels = next(rows)
        for column in column_labels:
            table.add_column(column, key=column)
        for index, row in enumerate(rows):
            table.add_row(*row, label=str(index))


app = TableApp()
if __name__ == "__main__":
    app.run()
