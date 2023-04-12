from textual.app import App, ComposeResult
from textual.widgets import DataTable

data = [
    "Severance",
    "Foundation",
    "Dark",
    "The Boys",
    "The Last of Us",
    "Lost in Space",
    "Altered Carbon",
]


class DataTableCursorStyles(App):
    """Regression test snapshot app which ensures that styles
    are layered on top of each other correctly in the DataTable.
    In this example, the colour of the text in the cells under
    the cursor should not be red, because the CSS should be applied
    on top."""

    CSS = """
DataTable > .datatable--cursor {
    color: $text;
    background: $success;
    text-style: bold italic;
}
"""

    def compose(self) -> ComposeResult:
        table = DataTable()
        table.zebra_stripes = True
        table.add_column("Movies")
        for row in data:
            table.add_row(f"[red]{row}")
        table.focus()
        yield table
