from __future__ import annotations

from dataclasses import dataclass
from typing import NamedTuple

from rich._ratio import ratio_resolve

from ..geometry import Point, Region
from ..layout import Layout, OrderedRegion
from ..widget import Widget


@dataclass
class GridOptions:
    size: int | None = None
    fraction: int = 1
    minimum_size: int = 1
    name: str | None = None

    @property
    def ratio(self) -> int:
        return self.fraction


class GridArea(NamedTuple):
    col_start: str
    col_end: str
    row_start: str
    row_end: str


class GridLayout(Layout):
    def __init__(self) -> None:
        self.columns: list[GridOptions] = []
        self.rows: list[GridOptions] = []
        self.areas: dict[str, GridArea] = {}
        self.widgets: dict[Widget, str | None] = {}
        super().__init__()

    def add_column(
        self,
        *,
        size: int | None = None,
        fraction: int = 1,
        minimum_size: int = 1,
        name: str | None = None,
    ) -> None:
        options = GridOptions(
            size=size, fraction=fraction, minimum_size=minimum_size, name=name
        )
        self.columns.append(options)

    def add_row(
        self,
        *,
        size: int | None = None,
        fraction: int = 1,
        minimum_size: int = 1,
        name: str | None = None,
    ) -> None:
        options = GridOptions(
            size=size, fraction=fraction, minimum_size=minimum_size, name=name
        )
        self.rows.append(options)

    def add_area(
        self, name: str, columns: str | tuple[str, str], rows: str | tuple[str, str]
    ):
        if isinstance(columns, str):
            column_start = f"{columns}-start"
            column_end = f"{columns}-end"
        else:
            column_start, column_end = columns

        if isinstance(rows, str):
            row_start = f"{rows}-start"
            row_end = f"{rows}-end"
        else:
            row_start, row_end = rows

        area = GridArea(column_start, column_end, row_start, row_end)
        self.areas[name] = area

    def add_widget(self, widget: Widget, area: str | None = None) -> Widget:
        self.widgets[widget] = area
        return widget

    def generate_map(
        self, width: int, height: int, offset: Point = Point(0, 0)
    ) -> dict[Widget, OrderedRegion]:
        def resolve(size, edges) -> list[int]:
            sizes = ratio_resolve(size, edges)
            total = 0
            for _size in sizes:
                total += _size
                yield total

        columns = [
            ("", 0),
            *(
                (column.name, column_width)
                for column, column_width in zip(
                    self.columns, resolve(width, self.columns)
                )
            ),
        ]
        column_tracks = {}
        for (_, track1), (name2, track2) in zip(columns, columns[1:]):
            column_tracks[f"{name2}-end"] = track2
            column_tracks[f"{name2}-start"] = track1

        rows = [
            ("", 0),
            *(
                (row.name, column_height)
                for row, column_height in zip(self.rows, resolve(height, self.rows))
            ),
        ]
        row_tracks = {}
        for (_, track1), (name2, track2) in zip(rows, rows[1:]):
            row_tracks[f"{name2}-end"] = track2
            row_tracks[f"{name2}-start"] = track1

        order = 1

        map = {}
        for widget, area in self.widgets.items():
            if not area:
                continue
            column_start, column_end, row_start, row_end = self.areas[area]
            x1 = column_tracks[column_start]
            x2 = column_tracks[column_end]
            y1 = row_tracks[row_start]
            y2 = row_tracks[row_end]
            map[widget] = OrderedRegion(Region.from_corners(x1, y1, x2, y2), (0, order))
            order += 1

        return map


if __name__ == "__main__":
    layout = GridLayout()
    layout.add_column(size=20, name="left")
    layout.add_column(fraction=2, name="middle")
    layout.add_column(fraction=1, name="right")

    layout.add_row(fraction=1, name="top")
    layout.add_row(fraction=2, name="bottom")

    layout.add_area("center", "middle", "top")

    from ..widgets import Static

    layout.add_widget(Static("foo"), "center")

    from rich import print

    print(layout.widgets)

    map = layout.generate_map(100, 80)
    print(map)