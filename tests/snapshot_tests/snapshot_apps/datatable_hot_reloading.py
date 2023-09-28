from pathlib import Path

from textual.app import App, ComposeResult
from textual.widgets import DataTable

CSS_PATH = (Path(__file__) / "../datatable_hot_reloading.tcss").resolve()

# Write some CSS to the file before the app loads.
# Then, the test will clear all the CSS to see if the
# hot reloading applies the changes correctly.
CSS_PATH.write_text(
    """\
DataTable > .datatable--cursor {
    background: purple;
}

DataTable > .datatable--fixed {
    background: red;
}

DataTable > .datatable--fixed-cursor {
    background: blue;
}

DataTable > .datatable--header {
    background: yellow;
}

DataTable > .datatable--odd-row {
    background: pink;
}

DataTable > .datatable--even-row {
    background: brown;
}
"""
)


class DataTableHotReloadingApp(App[None]):
    CSS_PATH = CSS_PATH

    def compose(self) -> ComposeResult:
        yield DataTable(zebra_stripes=True, cursor_type="row")

    def on_mount(self) -> None:
        dt = self.query_one(DataTable)
        dt.add_column("A", width=10)
        self.c = dt.add_column("B")
        dt.fixed_columns = 1
        dt.add_row("one", "two")
        dt.add_row("three", "four")
        dt.add_row("five", "six")


if __name__ == "__main__":
    app = DataTableHotReloadingApp()
    app.run()
