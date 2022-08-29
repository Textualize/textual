from __future__ import annotations

from fractions import Fraction
from typing import TYPE_CHECKING, Iterable

from .._layout import ArrangeResult, Layout, WidgetPlacement
from .._resolve import resolve
from ..css.scalar import Scalar
from ..geometry import Region, Size

if TYPE_CHECKING:
    from ..widget import Widget


class TableLayout(Layout):
    """Used to layout Widgets vertically on screen, from top to bottom."""

    name = "table"

    def arrange(
        self, parent: Widget, children: list[Widget], size: Size
    ) -> ArrangeResult:
        styles = parent.styles
        row_scalars = styles.table_rows or [Scalar.parse("1fr")]
        column_scalars = styles.table_columns or [Scalar.parse("1fr")]
        gutter_horizontal = styles.table_gutter_horizontal
        gutter_vertical = styles.table_gutter_vertical
        viewport = parent.screen.size

        def cell_coords(column_count: int, row_count: int) -> Iterable[tuple[int, int]]:
            """Iterate over table coordinates.

            Args:
                column_count (int): Number of columns
                row_count (int): Number of row

            """
            for row in range(row_count):
                for column in range(column_count):
                    yield (column, row)

        def widget_coords(
            col_start: int, row_start: int, columns: int, rows: int
        ) -> set[tuple[int, int]]:
            """Get coords occupied by a cell."""
            return {
                (column, row)
                for column in range(col_start, col_start + columns)
                for row in range(row_start, row_start + rows)
            }

        cell_map: dict[tuple[int, int], tuple[Widget, bool]] = {}
        cell_size_map: dict[Widget, tuple[int, int, int, int]] = {}

        column_count = len(column_scalars)
        row_count = len(row_scalars)
        next_coord = iter(cell_coords(column_count, row_count)).__next__
        cell_coord = (0, 0)
        try:
            for child in children:
                child_styles = child.styles
                column_span = child_styles.column_span or 1
                row_span = child_styles.row_span or 1
                while True:
                    column, row = cell_coord
                    coords = widget_coords(column, row, column_span, row_span)
                    if cell_map.keys().isdisjoint(coords):
                        for coord in coords:
                            cell_map[coord] = (child, coord == cell_coord)
                        cell_size_map[child] = (
                            column,
                            row,
                            column_span - 1,
                            row_span - 1,
                        )
                        break
                    else:
                        cell_coord = next_coord()
                        continue
                cell_coord = next_coord()
        except StopIteration:
            pass

        columns = resolve(column_scalars, size.width, gutter_vertical, size, viewport)
        rows = resolve(row_scalars, size.height, gutter_horizontal, size, viewport)

        placements: list[WidgetPlacement] = []
        add_placement = placements.append
        fraction_unit = Fraction(1)
        max_column = column_count - 1
        max_row = row_count - 1
        for widget, (column, row, column_span, row_span) in cell_size_map.items():
            x = columns[column][0]
            y = rows[row][0]
            x2, cell_width = columns[min(max_column, column + column_span)]
            y2, cell_height = rows[min(max_row, row + row_span)]

            width, height, margin = widget._get_box_model(
                Size(x2 - x + cell_width, y2 - y + cell_height),
                viewport,
                fraction_unit,
            )
            region = Region(x, y, int(width), int(height)).shrink(margin)
            add_placement(WidgetPlacement(region, widget))

        return placements, set(cell_size_map.keys())
