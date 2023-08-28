from rich.text import Text

from textual.app import App, ComposeResult
from textual.events import Click
from textual.widgets import DataTable, Footer

ROWS = [
    ("lane", "swimmer", "country", "time 1", "time 2"),
    (4, "Joseph Schooling", Text("Singapore", style="italic"), 50.39, 51.84),
    (2, "Michael Phelps", Text("United States", style="italic"), 51.14, 51.84),
    (5, "Chad le Clos", Text("South Africa", style="italic"), 51.14, 51.73),
    (6, "László Cseh", Text("Hungary", style="italic"), 51.14, 51.58),
    (3, "Li Zhuhao", Text("China", style="italic"), 51.26, 51.26),
    (8, "Mehdy Metella", Text("France", style="italic"), 51.58, 52.15),
    (7, "Tom Shields", Text("United States", style="italic"), 51.73, 51.12),
    (1, "Aleksandr Sadovnikov", Text("Russia", style="italic"), 51.84, 50.85),
    (10, "Darren Burns", Text("Scotland", style="italic"), 51.84, 51.55),
]


class TableApp(App):
    BINDINGS = [
        ("a", "sort_by_average_time", "Sort By Average Time"),
        ("n", "sort_by_last_name", "Sort By Last Name"),
        ("c", "sort_by_country", "Sort By Country"),
    ]

    current_sorts: set = set()

    def compose(self) -> ComposeResult:
        yield DataTable()
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        for col in ROWS[0]:
            table.add_column(col, key=col)
        table.add_rows(ROWS[1:])

    def sort_reverse(self, sort_type: str):
        """Determine if `sort_type` is ascending or descending."""
        reverse = sort_type in self.current_sorts
        if reverse:
            self.current_sorts.remove(sort_type)
        else:
            self.current_sorts.add(sort_type)
        return reverse

    def action_sort_by_average_time(self) -> None:
        """Sort DataTable by average of times (via a function) and
        passing of column data through positional arguments."""

        def sort_by_average_time(times):
            return sum(n for n in times) / len(times)

        table = self.query_one(DataTable)
        table.sort(
            "time 1",
            "time 2",
            key=sort_by_average_time,
            reverse=self.sort_reverse("time"),
        )

    def action_sort_by_last_name(self) -> None:
        """Sort DataTable by last name of swimmer (via a lambda)."""
        table = self.query_one(DataTable)
        table.sort(
            key=lambda row: row[1]["swimmer"].split()[-1],
            reverse=self.sort_reverse("swimmer"),
        )

    def action_sort_by_country(self) -> None:
        """Sort DataTable by country which is a `Rich.Text` object."""
        table = self.query_one(DataTable)
        table.sort(
            "country",
            key=lambda country: country.plain,
            reverse=self.sort_reverse("country"),
        )

    def on_data_table_header_selected(self, event: Click) -> None:
        """Sort `DataTable` items by the clicked column header."""

        def sort_by_plain_text(cell):
            return cell.plain if isinstance(cell, Text) else cell

        column_key = event.column_key
        table = self.query_one(DataTable)
        table.sort(
            column_key, key=sort_by_plain_text, reverse=self.sort_reverse(column_key)
        )


app = TableApp()
if __name__ == "__main__":
    app.run()
