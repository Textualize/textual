from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from itertools import cycle
import sys
from typing import Iterable, NamedTuple

from .._layout_resolve import layout_resolve
from .._loop import loop_last
from ..geometry import Dimensions, Point, Region
from ..layout import Layout, OrderedRegion
from ..widget import Widget

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal


GridAlign = Literal["start", "end", "center", "stretch"]


@dataclass
class GridOptions:
    size: int | None = None
    fraction: int = 1
    min_size: int = 1
    max_size: int | None = None
    name: str | None = None


class GridArea(NamedTuple):
    col_start: str
    col_end: str
    row_start: str
    row_end: str


class GridLayout(Layout):
    def __init__(
        self,
        gap: tuple[int, int] | int | None = None,
        gutter: tuple[int, int] | int | None = None,
        align: tuple[GridAlign, GridAlign] | None = None,
    ) -> None:
        self.columns: list[GridOptions] = []
        self.rows: list[GridOptions] = []
        self.areas: dict[str, GridArea] = {}
        self.widgets: dict[Widget, str | None] = {}
        self.column_gap = 1
        self.row_gap = 1
        self.column_repeat = False
        self.row_repeat = False
        self.column_align: GridAlign = "start"
        self.row_align: GridAlign = "start"
        self.column_gutter: int = 0
        self.row_gutter: int = 0

        if gap is not None:
            if isinstance(gap, tuple):
                self.set_gap(*gap)
            else:
                self.set_gap(gap)

        if gutter is not None:
            if isinstance(gutter, tuple):
                self.set_gutter(*gutter)
            else:
                self.set_gutter(gutter)

        if align is not None:
            self.set_align(*align)

        super().__init__()

    def add_column(
        self,
        *,
        size: int | None = None,
        fraction: int = 1,
        min_size: int = 1,
        max_size: int | None = None,
        name: str | None = None,
        repeat: int = 1,
    ) -> None:
        names = (
            [name]
            if repeat == 1
            else [f"{name}{count}" for count in range(1, repeat + 1)]
        )
        append = self.columns.append
        for name in names:
            append(
                GridOptions(
                    size=size,
                    fraction=fraction,
                    min_size=min_size,
                    max_size=max_size,
                    name=name,
                )
            )

    def add_row(
        self,
        *,
        size: int | None = None,
        fraction: int = 1,
        min_size: int = 1,
        max_size: int | None = None,
        name: str | None = None,
        repeat: int = 1,
    ) -> None:
        names = (
            [name]
            if repeat == 1
            else [f"{name}{count}" for count in range(1, repeat + 1)]
        )
        append = self.rows.append
        for name in names:
            append(
                GridOptions(
                    size=size,
                    fraction=fraction,
                    min_size=min_size,
                    max_size=max_size,
                    name=name,
                )
            )

    def _add_area(
        self, name: str, columns: str | tuple[str, str], rows: str | tuple[str, str]
    ) -> None:
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

        self.areas[name] = GridArea(column_start, column_end, row_start, row_end)

    def add_areas(self, **areas: str) -> None:
        for name, area in areas.items():
            area = area.replace(" ", "")
            column, _, row = area.partition(",")

            column_start, column_sep, column_end = column.partition("|")
            row_start, row_sep, row_end = row.partition("|")

            self._add_area(
                name,
                (column_start, column_end) if column_sep else column,
                (row_start, row_end) if row_sep else row,
            )

    def set_gap(self, column: int, row: int | None = None) -> None:
        self.column_gap = column
        self.row_gap = column if row is None else row

    def set_gutter(self, column: int, row: int | None = None) -> None:
        self.column_gutter = column
        self.row_gutter = column if row is None else row

    def add_widget(self, widget: Widget, area: str | None = None) -> Widget:
        self.widgets[widget] = area
        return widget

    def place(self, *auto_widgets: Widget, **area_widgets: Widget) -> None:
        widgets = self.widgets
        for area, widget in area_widgets.items():
            widgets[widget] = area
        for widget in auto_widgets:
            widgets[widget] = None

    def set_repeat(self, column: bool | None = None, row: bool | None = None) -> None:
        if column is not None:
            self.column_repeat = column
        if row is not None:
            self.row_repeat = row

    def set_align(self, column: GridAlign | None = None, row: GridAlign | None = None):
        if column is not None:
            self.column_align = column
        if row is not None:
            self.row_align = row

    @classmethod
    def _align(
        cls,
        region: Region,
        grid_size: Dimensions,
        container: Dimensions,
        col_align: GridAlign,
        row_align: GridAlign,
    ) -> Region:
        offset_x = 0
        offset_y = 0

        def align(size: int, container: int, align: GridAlign) -> int:
            offset = 0
            if align == "end":
                offset = container - size
            elif align == "center":
                offset = (container - size) // 2
            return offset

        size = region.size
        offset_x = align(grid_size.width, container.width, col_align)
        offset_y = align(grid_size.height, container.height, row_align)

        region = region.translate(offset_x, offset_y)
        return region

    def generate_map(
        self, width: int, height: int, offset: Point = Point(0, 0)
    ) -> dict[Widget, OrderedRegion]:
        def resolve(
            size: int, edges: list[GridOptions], gap: int, repeat: bool
        ) -> Iterable[tuple[int, int]]:
            tracks = [
                track if edge.max_size is None else min(edge.max_size, track)
                for track, edge in zip(layout_resolve(size, edges), edges)
            ]
            if repeat:
                tracks = cycle(tracks)
            total = 0
            for index, track in enumerate(tracks):
                yield total, total + track - gap if total + track < size else total + track
                total += track
                if total >= size and index >= len(edges):
                    break

        def resolve_tracks(
            grid: list[GridOptions], size: int, gap: int, repeat: bool
        ) -> tuple[dict[str, list[int]], int]:
            spans = (
                (options.name, span)
                for options, span in zip(cycle(grid), resolve(size, grid, gap, repeat))
            )
            max_size = 0
            tracks: dict[str, list[int]] = defaultdict(list)
            for name, (start, end) in spans:
                max_size = max(max_size, end)
                tracks[f"{name}-start"].append(start)
                tracks[f"{name}-end"].append(end)
            return tracks, max_size

        container = Dimensions(
            width - self.column_gutter * 2, height - self.row_gutter * 2
        )
        column_tracks, column_size = resolve_tracks(
            self.columns, container.width, self.column_gap, self.column_repeat
        )
        row_tracks, row_size = resolve_tracks(
            self.rows, container.height, self.row_gap, self.row_repeat
        )
        grid_size = Dimensions(column_size, row_size)

        widget_areas = (
            (widget, area)
            for widget, area in self.widgets.items()
            if area and widget.visible
        )

        map = {}
        order = 1
        from_corners = Region.from_corners
        gutter = Point(self.column_gutter, self.row_gutter)
        for widget, area in widget_areas:
            column_start, column_end, row_start, row_end = self.areas[area]
            try:
                x1 = column_tracks[column_start][0]
                x2 = column_tracks[column_end][0]
                y1 = row_tracks[row_start][0]
                y2 = row_tracks[row_end][0]
            except (KeyError, IndexError):
                continue

            region = self._align(
                from_corners(x1, y1, x2, y2),
                grid_size,
                container,
                self.column_align,
                self.row_align,
            )
            map[widget] = OrderedRegion(region + gutter, (0, order))
            order += 1

        # Widgets with no area assigned.
        auto_widgets = [widget for widget, area in self.widgets.items() if area is None]

        return map


if __name__ == "__main__":
    layout = GridLayout()

    layout.add_column(size=20, name="a")
    layout.add_column(size=10, name="b")

    layout.add_row(fraction=1, name="top")
    layout.add_row(fraction=2, name="bottom")

    layout.add_area("center", "middle", "top")

    from rich import print

    print(layout.widgets)

    map = layout.generate_map(100, 80)
    print(map)