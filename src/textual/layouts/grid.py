from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, NamedTuple

from .._layout_resolve import layout_resolve
from .._loop import loop_last
from ..geometry import Point, Region
from ..layout import Layout, OrderedRegion
from ..widget import Widget


@dataclass
class GridOptions:
    size: int | None = None
    fraction: int = 1
    minimum_size: int = 1
    maximum_size: int | None = None
    name: str | None = None


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
        self.column_gap = 1
        self.row_gap = 1
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

    def set_gaps(self, column: int, row: int | None) -> None:
        self.column_gap = column
        self.row_gap = column if row is None else row

    def add_widget(self, widget: Widget, area: str | None = None) -> Widget:
        self.widgets[widget] = area
        return widget

    def generate_map(
        self, width: int, height: int, offset: Point = Point(0, 0)
    ) -> dict[Widget, OrderedRegion]:
        def resolve(
            size: int, edges: list[GridOptions], gap: int
        ) -> Iterable[tuple[int, int]]:
            tracks = [
                track if edge.maximum_size is None else min(edge.maximum_size, track)
                for track, edge in zip(layout_resolve(size, edges), edges)
            ]
            total = 0
            for last, track in loop_last(tracks):
                yield total, total + track if last else total + track - gap
                total += track

        def resolve_tracks(
            grid: list[GridOptions], size: int, gap: int
        ) -> dict[str, int]:
            spans = (
                (options.name, span)
                for options, span in zip(grid, resolve(size, grid, gap))
            )
            tracks: dict[str, int] = {}
            for name, (start, end) in spans:
                tracks[f"{name}-start"] = start
                tracks[f"{name}-end"] = end
            return tracks

        column_tracks = resolve_tracks(self.columns, width, self.column_gap)
        row_tracks = resolve_tracks(self.rows, height, self.row_gap)

        widget_areas = (
            (widget, area)
            for widget, area in self.widgets.items()
            if area and widget.visible
        )

        map = {}
        order = 1
        from_corners = Region.from_corners
        for widget, area in widget_areas:
            column_start, column_end, row_start, row_end = self.areas[area]
            x1 = column_tracks[column_start]
            x2 = column_tracks[column_end]
            y1 = row_tracks[row_start]
            y2 = row_tracks[row_end]
            map[widget] = OrderedRegion(from_corners(x1, y1, x2, y2), (0, order))
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