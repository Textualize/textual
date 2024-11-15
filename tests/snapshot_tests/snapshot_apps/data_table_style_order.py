from typing_extensions import Literal

from textual.app import App, ComposeResult
from textual.widgets import DataTable, Label

data = [
    "Severance",
    "Foundation",
    "Dark",
]


def make_datatable(
    foreground_priority: Literal["css", "renderable"],
    background_priority: Literal["css", "renderable"],
) -> DataTable:
    table = DataTable(
        cursor_foreground_priority=foreground_priority,
        cursor_background_priority=background_priority,
    )
    table.zebra_stripes = True
    table.add_column("Movies")
    for row in data:
        table.add_row(f"[red on blue]{row}")
    return table


class DataTableCursorStyles(App):
    """Regression test snapshot app which ensures that styles
    are layered on top of each other correctly in the DataTable.
    In this example, the colour of the text in the cells under
    the cursor should not be red, because the CSS should be applied
    on top."""

    CSS = """
    DataTable {margin-bottom: 1;}
    DataTable > .datatable--cursor {
        color: $accent;
        background: $success;
        text-style: bold italic;
    }
"""

    def compose(self) -> ComposeResult:
        priorities: list[
            tuple[Literal["css", "renderable"], Literal["css", "renderable"]]
        ] = [
            ("css", "css"),
            ("css", "renderable"),
            ("renderable", "renderable"),
            ("renderable", "css"),
        ]
        for foreground, background in priorities:
            yield Label(f"Foreground is {foreground!r}, background is {background!r}:")
            table = make_datatable(foreground, background)
            yield table


app = DataTableCursorStyles()

if __name__ == "__main__":
    app.run()
