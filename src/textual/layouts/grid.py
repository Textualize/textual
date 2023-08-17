from __future__ import annotations

from fractions import Fraction
from typing import TYPE_CHECKING, Iterable

from .._layout import ArrangeResult, Layout, WidgetPlacement
from .._resolve import resolve
from ..css.scalar import Scalar
from ..geometry import Region, Size, Spacing

if TYPE_CHECKING:
    from ..widget import Widget


class GridLayout(Layout):
    """Used to layout Widgets in to a grid."""

    name = "grid"

    def arrange(
        self, parent: Widget, children: list[Widget], size: Size
    ) -> ArrangeResult:
        styles = parent.styles
        row_scalars = styles.grid_rows or (
            [Scalar.parse("1fr")] if size.height else [Scalar.parse("auto")]
        )
        column_scalars = styles.grid_columns or [Scalar.parse("1fr")]
        gutter_horizontal = styles.grid_gutter_horizontal
        gutter_vertical = styles.grid_gutter_vertical
        table_size_columns = max(1, styles.grid_size_columns)
        table_size_rows = styles.grid_size_rows
        viewport = parent.screen.size

        def cell_coords(column_count: int) -> Iterable[tuple[int, int]]:
            """Iterate over table coordinates ad infinitum.

            Args:
                column_count: Number of columns
            """
            row = 0
            while True:
                for column in range(column_count):
                    yield (column, row)
                row += 1

        def widget_coords(
            column_start: int, row_start: int, columns: int, rows: int
        ) -> set[tuple[int, int]]:
            """Get coords occupied by a cell.

            Args:
                column_start: Start column.
                row_start: Start_row.
                columns: Number of columns.
                rows: Number of rows.

            Returns:
                Set of coords.
            """
            return {
                (column, row)
                for column in range(column_start, column_start + columns)
                for row in range(row_start, row_start + rows)
            }

        def repeat_scalars(scalars: Iterable[Scalar], count: int) -> list[Scalar]:
            """Repeat an iterable of scalars as many times as required to return
            a list of `count` values.

            Args:
                scalars: Iterable of values.
                count: Number of values to return.

            Returns:
                A list of values.
            """
            limited_values = list(scalars)[:]
            while len(limited_values) < count:
                limited_values.extend(scalars)
            return limited_values[:count]

        cell_map: dict[tuple[int, int], tuple[Widget, bool]] = {}
        cell_size_map: dict[Widget, tuple[int, int, int, int]] = {}

        column_count = table_size_columns
        next_coord = iter(cell_coords(column_count)).__next__
        cell_coord = (0, 0)
        column = row = 0

        for child in children:
            child_styles = child.styles
            column_span = child_styles.column_span or 1
            row_span = child_styles.row_span or 1
            # Find a slot where this cell fits
            # A cell on a previous row may have a row span
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

        column_scalars = repeat_scalars(column_scalars, table_size_columns)
        row_scalars = repeat_scalars(
            row_scalars, table_size_rows if table_size_rows else row + 1
        )

        def apply_width_limits(widget: Widget, width: int) -> int:
            """Apply min and max widths to dimension.

            Args:
                widget: A Widget.
                width: A width.

            Returns:
                New width.
            """
            styles = widget.styles
            if styles.min_width is not None:
                width = max(
                    width,
                    int(styles.min_width.resolve(size, viewport, Fraction(width))),
                )
            if styles.max_width is not None:
                width = min(
                    width,
                    int(styles.max_width.resolve(size, viewport, Fraction(width))),
                )
            return width

        def apply_height_limits(widget: Widget, height: int) -> int:
            """Apply min and max height to a dimension.

            Args:
                widget: A widget.
                height: A height.

            Returns:
                New height
            """
            styles = widget.styles
            if styles.min_height is not None:
                height = max(
                    height,
                    int(styles.min_height.resolve(size, viewport, Fraction(height))),
                )
            if styles.max_height is not None:
                height = min(
                    height,
                    int(styles.max_height.resolve(size, viewport, Fraction(height))),
                )
            return height

        # Handle any auto columns
        for column, scalar in enumerate(column_scalars):
            if scalar.is_auto:
                width = 0.0
                for row in range(len(row_scalars)):
                    coord = (column, row)
                    try:
                        widget, _ = cell_map[coord]
                    except KeyError:
                        pass
                    else:
                        if widget.styles.column_span != 1:
                            continue
                        width = max(
                            width,
                            apply_width_limits(
                                widget,
                                widget.get_content_width(size, viewport)
                                + widget.styles.gutter.width,
                            ),
                        )
                column_scalars[column] = Scalar.from_number(width)

        columns = resolve(column_scalars, size.width, gutter_vertical, size, viewport)

        # Handle any auto rows
        for row, scalar in enumerate(row_scalars):
            if scalar.is_auto:
                height = 0.0
                for column in range(len(column_scalars)):
                    coord = (column, row)
                    try:
                        widget, _ = cell_map[coord]
                    except KeyError:
                        pass
                    else:
                        if widget.styles.row_span != 1:
                            continue
                        column_width = columns[column][1]
                        widget_height = apply_height_limits(
                            widget,
                            widget.get_content_height(
                                size,
                                viewport,
                                column_width - parent.styles.grid_gutter_vertical,
                            )
                            + widget.styles.gutter.height,
                        )
                        height = max(height, widget_height)
                row_scalars[row] = Scalar.from_number(height)

        rows = resolve(row_scalars, size.height, gutter_horizontal, size, viewport)

        placements: list[WidgetPlacement] = []
        add_placement = placements.append
        widgets: list[Widget] = []
        add_widget = widgets.append
        max_column = len(columns) - 1
        max_row = len(rows) - 1
        margin = Spacing()
        for widget, (column, row, column_span, row_span) in cell_size_map.items():
            x = columns[column][0]
            if row > max_row:
                break
            y = rows[row][0]
            x2, cell_width = columns[min(max_column, column + column_span)]
            y2, cell_height = rows[min(max_row, row + row_span)]
            cell_size = Size(cell_width + x2 - x, cell_height + y2 - y)
            width, height, margin = widget._get_box_model(
                cell_size,
                viewport,
                Fraction(cell_size.width),
                Fraction(cell_size.height),
            )
            region = (
                Region(x, y, int(width + margin.width), int(height + margin.height))
                .shrink(margin)
                .clip_size(cell_size)
            )
            add_placement(WidgetPlacement(region, margin, widget))
            add_widget(widget)

        return placements
