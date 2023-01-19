from __future__ import annotations

from dataclasses import dataclass, field
from itertools import chain, zip_longest
from typing import ClassVar, Generic, Iterable, TypeVar, cast

import rich.repr
from rich.console import RenderableType
from rich.padding import Padding
from rich.protocol import is_renderable
from rich.segment import Segment
from rich.style import Style
from rich.text import Text, TextType

from .. import events, messages
from .._cache import LRUCache
from .._segment_tools import line_crop
from .._types import SegmentLines
from .._typing import Literal
from ..binding import Binding
from ..coordinate import Coordinate
from ..geometry import Region, Size, Spacing, clamp
from ..message import Message
from ..reactive import Reactive
from ..render import measure
from ..scroll_view import ScrollView
from ..strip import Strip

CursorType = Literal["cell", "row", "column", "none"]
CELL: CursorType = "cell"
CellType = TypeVar("CellType")


class CellDoesNotExist(Exception):
    pass


def default_cell_formatter(obj: object) -> RenderableType | None:
    """Format a cell in to a renderable.

    Args:
        obj: Data for a cell.

    Returns:
        A renderable or None if the object could not be rendered.
    """
    if isinstance(obj, str):
        return Text.from_markup(obj)
    if not is_renderable(obj):
        return None
    return cast(RenderableType, obj)


@dataclass
class Column:
    """Table column."""

    label: Text
    width: int = 0
    visible: bool = False
    index: int = 0

    content_width: int = 0
    auto_width: bool = False

    @property
    def render_width(self) -> int:
        """int: Width in cells, required to render a column."""
        # +2 is to account for space padding either side of the cell
        if self.auto_width:
            return self.content_width + 2
        else:
            return self.width + 2


@dataclass
class Row:
    """Table row."""

    index: int
    height: int
    y: int
    cell_renderables: list[RenderableType] = field(default_factory=list)


class DataTable(ScrollView, Generic[CellType], can_focus=True):
    DEFAULT_CSS = """
    App.-dark DataTable {
        background:;
    }
    DataTable {
        background: $surface ;
        color: $text;
    }
    DataTable > .datatable--header {
        text-style: bold;
        background: $primary;
        color: $text;
    }
    DataTable > .datatable--fixed {
        text-style: bold;
        background: $primary;
        color: $text;
    }

    DataTable > .datatable--odd-row {

    }

    DataTable > .datatable--even-row {
        background: $primary 10%;
    }

    DataTable >  .datatable--cursor {
        background: $secondary;
        color: $text;
    }

    DataTable > .datatable--cursor-fixed {
        background: $secondary-darken-1;
        color: $text;
    }

    DataTable > .datatable--highlight-fixed {
        background: $secondary 30%;
    }

    .-dark-mode DataTable > .datatable--even-row {
        background: $primary 15%;
    }

    DataTable > .datatable--highlight {
        background: $secondary 20%;
    }
    """

    COMPONENT_CLASSES: ClassVar[set[str]] = {
        "datatable--header",
        "datatable--cursor-fixed",
        "datatable--highlight-fixed",
        "datatable--fixed",
        "datatable--odd-row",
        "datatable--even-row",
        "datatable--highlight",
        "datatable--cursor",
    }

    BINDINGS = [
        Binding("enter", "select_cursor", "Select", show=False),
        Binding("up", "cursor_up", "Cursor Up", show=False),
        Binding("down", "cursor_down", "Cursor Down", show=False),
        Binding("right", "cursor_right", "Cursor Right", show=False),
        Binding("left", "cursor_left", "Cursor Left", show=False),
    ]

    show_header = Reactive(True)
    fixed_rows = Reactive(0)
    fixed_columns = Reactive(0)
    zebra_stripes = Reactive(False)
    header_height = Reactive(1)
    show_cursor = Reactive(True)
    cursor_type = Reactive(CELL)

    cursor_cell: Reactive[Coordinate] = Reactive(
        Coordinate(0, 0), repaint=False, always_update=True
    )
    hover_cell: Reactive[Coordinate] = Reactive(Coordinate(0, 0), repaint=False)

    def __init__(
        self,
        *,
        show_header: bool = True,
        fixed_rows: int = 0,
        fixed_columns: int = 0,
        zebra_stripes: bool = False,
        header_height: int = 1,
        show_cursor: bool = True,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)

        self.columns: list[Column] = []
        self.rows: dict[int, Row] = {}
        self.data: dict[int, list[CellType]] = {}
        self.row_count = 0
        self._y_offsets: list[tuple[int, int]] = []
        self._row_render_cache: LRUCache[
            tuple[int, int, Style, int, int], tuple[SegmentLines, SegmentLines]
        ]
        self._row_render_cache = LRUCache(1000)
        self._cell_render_cache: LRUCache[
            tuple[int, int, Style, bool, bool], SegmentLines
        ]
        self._cell_render_cache = LRUCache(10000)
        self._line_cache: LRUCache[tuple[int, int, int, int, int, int, Style], Strip]
        self._line_cache = LRUCache(1000)

        self._line_no = 0
        self._require_update_dimensions: bool = False
        self._new_rows: set[int] = set()

        self.show_header = show_header
        self.fixed_rows = fixed_rows
        self.fixed_columns = fixed_columns
        self.zebra_stripes = zebra_stripes
        self.header_height = header_height
        self.show_cursor = show_cursor
        self._show_hover_cursor = False

    @property
    def hover_row(self) -> int:
        return self.hover_cell.row

    @property
    def hover_column(self) -> int:
        return self.hover_cell.column

    @property
    def cursor_row(self) -> int:
        return self.cursor_cell.row

    @property
    def cursor_column(self) -> int:
        return self.cursor_cell.column

    def get_cell_value(self, coordinate: Coordinate) -> CellType:
        """Get the value from the cell at the given coordinate.

        Args:
            coordinate: The coordinate to retrieve the value from.

        Returns:
            The value of the cell.

        Raises:
            CellDoesNotExist: If there is no cell with the given coordinate.
        """
        row, column = coordinate
        try:
            cell_value = self.data[row][column]
        except KeyError:
            raise CellDoesNotExist(f"No cell exists at {coordinate!r}") from None
        return cell_value

    def _clear_caches(self) -> None:
        self._row_render_cache.clear()
        self._cell_render_cache.clear()
        self._line_cache.clear()
        self._styles_cache.clear()

    def get_row_height(self, row_index: int) -> int:
        if row_index == -1:
            return self.header_height
        return self.rows[row_index].height

    async def on_styles_updated(self, message: messages.StylesUpdated) -> None:
        self._clear_caches()
        self.refresh()

    def watch_show_cursor(self, show_cursor: bool) -> None:
        self._clear_caches()
        if show_cursor and self.cursor_type != "none":
            # When we re-enable the cursor, apply highlighting and
            # emit the appropriate [Row|Column|Cell]Highlighted event.
            self._scroll_cursor_into_view(animate=False)
            if self.cursor_type == "cell":
                self._highlight_cell(self.cursor_cell)
            elif self.cursor_type == "row":
                self._highlight_row(self.cursor_row)
            elif self.cursor_type == "column":
                self._highlight_column(self.cursor_column)

    def watch_show_header(self, show_header: bool) -> None:
        self._clear_caches()

    def watch_fixed_rows(self, fixed_rows: int) -> None:
        self._clear_caches()

    def watch_zebra_stripes(self, zebra_stripes: bool) -> None:
        self._clear_caches()

    def watch_hover_cell(self, old: Coordinate, value: Coordinate) -> None:
        self.refresh_cell(*old)
        self.refresh_cell(*value)

    def watch_cursor_cell(
        self, old_coordinate: Coordinate, new_coordinate: Coordinate
    ) -> None:
        if old_coordinate != new_coordinate:
            # Refresh the old and the new cell, and emit the appropriate
            # message to tell users of the newly highlighted row/cell/column.
            if self.cursor_type == "cell":
                self.refresh_cell(*old_coordinate)
                self._highlight_cell(new_coordinate)
            elif self.cursor_type == "row":
                self.refresh_row(old_coordinate.row)
                self._highlight_row(new_coordinate.row)
            elif self.cursor_type == "column":
                self.refresh_column(old_coordinate.column)
                self._highlight_column(new_coordinate.column)

    def _highlight_cell(self, coordinate: Coordinate) -> None:
        """Apply highlighting to the cell at the coordinate, and emit event."""
        self.refresh_cell(*coordinate)
        try:
            cell_value = self.get_cell_value(coordinate)
        except CellDoesNotExist:
            # The cell may not exist e.g. when the table is cleared.
            # In that case, there's nothing for us to do here.
            return
        else:
            self.emit_no_wait(DataTable.CellHighlighted(self, cell_value, coordinate))

    def _highlight_row(self, row_index: int) -> None:
        """Apply highlighting to the row at the given index, and emit event."""
        self.refresh_row(row_index)
        if row_index in self.data:
            self.emit_no_wait(DataTable.RowHighlighted(self, row_index))

    def _highlight_column(self, column_index: int) -> None:
        """Apply highlighting to the column at the given index, and emit event."""
        self.refresh_column(column_index)
        if column_index < len(self.columns):
            self.emit_no_wait(DataTable.ColumnHighlighted(self, column_index))

    def validate_cursor_cell(self, value: Coordinate) -> Coordinate:
        return self._clamp_cursor_cell(value)

    def _clamp_cursor_cell(self, cursor_cell: Coordinate) -> Coordinate:
        row, column = cursor_cell
        row = clamp(row, 0, self.row_count - 1)
        column = clamp(column, self.fixed_columns, len(self.columns) - 1)
        return Coordinate(row, column)

    def watch_cursor_type(self, old: str, new: str) -> None:
        self._set_hover_cursor(False)
        if self.show_cursor:
            self._highlight_cursor()

        # Refresh cells that were previously impacted by the cursor
        # but may no longer be.
        row_index, column_index = self.cursor_cell
        if old == "cell":
            self.refresh_cell(row_index, column_index)
        elif old == "row":
            self.refresh_row(row_index)
        elif old == "column":
            self.refresh_column(column_index)

        self._scroll_cursor_into_view()

    def _highlight_cursor(self) -> None:
        row_index, column_index = self.cursor_cell
        cursor_type = self.cursor_type
        # Apply the highlighting to the newly relevant cells
        if cursor_type == "cell":
            self._highlight_cell(self.cursor_cell)
        elif cursor_type == "row":
            self._highlight_row(row_index)
        elif cursor_type == "column":
            self._highlight_column(column_index)

    def _update_dimensions(self, new_rows: Iterable[int]) -> None:
        """Called to recalculate the virtual (scrollable) size."""
        for row_index in new_rows:
            for column, renderable in zip(
                self.columns, self._get_row_renderables(row_index)
            ):
                content_width = measure(self.app.console, renderable, 1)
                column.content_width = max(column.content_width, content_width)

        self._clear_caches()
        total_width = sum(column.render_width for column in self.columns)
        header_height = self.header_height if self.show_header else 0
        self.virtual_size = Size(
            total_width,
            len(self._y_offsets) + header_height,
        )

    def _get_cell_region(self, row_index: int, column_index: int) -> Region:
        """Get the region of the cell at the given coordinate (row_index, column_index)"""
        if row_index not in self.rows:
            return Region(0, 0, 0, 0)
        row = self.rows[row_index]
        x = sum(column.render_width for column in self.columns[:column_index])
        width = self.columns[column_index].render_width
        height = row.height
        y = row.y
        if self.show_header:
            y += self.header_height
        cell_region = Region(x, y, width, height)
        return cell_region

    def _get_row_region(self, row_index: int) -> Region:
        """Get the region of the row at the given index."""
        rows = self.rows
        if row_index < 0 or row_index >= len(rows):
            return Region(0, 0, 0, 0)
        row = rows[row_index]
        row_width = sum(column.render_width for column in self.columns)
        y = row.y
        if self.show_header:
            y += self.header_height
        row_region = Region(0, y, row_width, row.height)
        return row_region

    def _get_column_region(self, column_index: int) -> Region:
        """Get the region of the column at the given index."""
        columns = self.columns
        if column_index < 0 or column_index >= len(columns):
            return Region(0, 0, 0, 0)

        x = sum(column.render_width for column in self.columns[:column_index])
        width = columns[column_index].render_width
        header_height = self.header_height if self.show_header else 0
        height = len(self._y_offsets) + header_height
        full_column_region = Region(x, 0, width, height)
        return full_column_region

    def clear(self, columns: bool = False) -> None:
        """Clear the table.

        Args:
            columns: Also clear the columns. Defaults to False.
        """
        self.row_count = 0
        self._clear_caches()
        self._y_offsets.clear()
        self.data.clear()
        self.rows.clear()
        if columns:
            self.columns.clear()
        self._line_no = 0
        self._require_update_dimensions = True
        self.cursor_cell = Coordinate(0, 0)
        self.hover_cell = Coordinate(0, 0)
        self.refresh()

    def add_columns(self, *labels: TextType) -> None:
        """Add a number of columns.

        Args:
            *labels: Column headers.
        """
        for label in labels:
            self.add_column(label, width=None)

    def add_column(self, label: TextType, *, width: int | None = None) -> None:
        """Add a column to the table.

        Args:
            label: A str or Text object containing the label (shown top of column).
            width: Width of the column in cells or None to fit content. Defaults to None.
        """
        text_label = Text.from_markup(label) if isinstance(label, str) else label

        content_width = measure(self.app.console, text_label, 1)
        if width is None:
            column = Column(
                text_label,
                content_width,
                index=len(self.columns),
                content_width=content_width,
                auto_width=True,
            )
        else:
            column = Column(
                text_label, width, content_width=content_width, index=len(self.columns)
            )

        self.columns.append(column)
        self._require_update_dimensions = True
        self.check_idle()

    def add_row(self, *cells: CellType, height: int = 1) -> None:
        """Add a row.

        Args:
            *cells: Positional arguments should contain cell data.
            height: The height of a row (in lines). Defaults to 1.
        """
        row_index = self.row_count

        self.data[row_index] = list(cells)
        self.rows[row_index] = Row(row_index, height, self._line_no)

        for line_no in range(height):
            self._y_offsets.append((row_index, line_no))

        self.row_count += 1
        self._line_no += height

        self._new_rows.add(row_index)
        self._require_update_dimensions = True
        self.cursor_cell = self.cursor_cell
        self.check_idle()

        # If a position has opened for the cursor to appear, where it previously
        # could not (e.g. when there's no data in the table), then a highlighted
        # event is emitted, since there's now a highlighted cell when there wasn't
        # before.
        cell_now_available = self.row_count == 1 and len(self.columns) > 0
        visible_cursor = self.show_cursor and self.cursor_type != "none"
        if cell_now_available and visible_cursor:
            self._highlight_cursor()

    def add_rows(self, rows: Iterable[Iterable[CellType]]) -> None:
        """Add a number of rows.

        Args:
            rows: Iterable of rows. A row is an iterable of cells.
        """
        for row in rows:
            self.add_row(*row)

    def on_idle(self) -> None:
        if self._require_update_dimensions:
            self._require_update_dimensions = False
            new_rows = self._new_rows.copy()
            self._new_rows.clear()
            self._update_dimensions(new_rows)
            self.refresh()

    def refresh_cell(self, row_index: int, column_index: int) -> None:
        """Refresh a cell.

        Args:
            row_index: Row index.
            column_index: Column index.
        """
        if row_index < 0 or column_index < 0:
            return
        region = self._get_cell_region(row_index, column_index)
        self._refresh_region(region)

    def refresh_row(self, row_index: int) -> None:
        """Refresh the row at the given index.

        Args:
            row_index: The index of the row to refresh.
        """
        if row_index < 0 or row_index >= len(self.rows):
            return

        region = self._get_row_region(row_index)
        self._refresh_region(region)

    def refresh_column(self, column_index: int) -> None:
        """Refresh the column at the given index.

        Args:
            column_index: The index of the column to refresh.
        """
        if column_index < 0 or column_index >= len(self.columns):
            return

        region = self._get_column_region(column_index)
        self._refresh_region(region)

    def _refresh_region(self, region: Region) -> None:
        """Refresh a region of the DataTable, if it's visible within
        the window. This method will translate the region to account
        for scrolling."""
        if not self.window_region.overlaps(region):
            return
        region = region.translate(-self.scroll_offset)
        self.refresh(region)

    def _get_row_renderables(self, row_index: int) -> list[RenderableType]:
        """Get renderables for the given row.

        Args:
            row_index: Index of the row.

        Returns:
            List of renderables
        """

        if row_index == -1:
            row = [column.label for column in self.columns]
            return row

        data = self.data.get(row_index)
        empty = Text()
        if data is None:
            return [empty for _ in self.columns]
        else:
            return [
                Text() if datum is None else default_cell_formatter(datum) or empty
                for datum, _ in zip_longest(data, range(len(self.columns)))
            ]

    def _render_cell(
        self,
        row_index: int,
        column_index: int,
        style: Style,
        width: int,
        cursor: bool = False,
        hover: bool = False,
    ) -> SegmentLines:
        """Render the given cell.

        Args:
            row_index: Index of the row.
            column_index: Index of the column.
            style: Style to apply.
            width: Width of the cell.
            cursor: Is this cell affected by cursor highlighting?
            hover: Is this cell affected by hover cursor highlighting?

        Returns:
            A list of segments per line.
        """
        is_header_row = row_index == -1

        # The header row *and* fixed columns both have a different style (blue bg)
        is_fixed_style = is_header_row or column_index < self.fixed_columns
        show_cursor = self.show_cursor

        if hover and show_cursor and self._show_hover_cursor:
            style += self.get_component_styles("datatable--highlight").rich_style
            if is_fixed_style:
                # Apply subtle variation in style for the fixed (blue background by default)
                # rows and columns affected by the cursor, to ensure we can still differentiate
                # between the labels and the data.
                style += self.get_component_styles(
                    "datatable--highlight-fixed"
                ).rich_style

        if cursor and show_cursor:
            style += self.get_component_styles("datatable--cursor").rich_style
            if is_fixed_style:
                style += self.get_component_styles("datatable--cursor-fixed").rich_style

        cell_key = (row_index, column_index, style, cursor, hover)
        if cell_key not in self._cell_render_cache:
            style += Style.from_meta({"row": row_index, "column": column_index})
            height = (
                self.header_height if is_header_row else self.rows[row_index].height
            )
            cell = self._get_row_renderables(row_index)[column_index]
            lines = self.app.console.render_lines(
                Padding(cell, (0, 1)),
                self.app.console.options.update_dimensions(width, height),
                style=style,
            )
            self._cell_render_cache[cell_key] = lines
        return self._cell_render_cache[cell_key]

    def _render_row(
        self,
        row_index: int,
        line_no: int,
        base_style: Style,
        cursor_location: Coordinate,
        hover_location: Coordinate,
    ) -> tuple[SegmentLines, SegmentLines]:
        """Render a row in to lines for each cell.

        Args:
            row_index: Index of the row.
            line_no: Line number (on screen, 0 is top)
            base_style: Base style of row.
            cursor_location: The location of the cursor in the DataTable.
            hover_location: The location of the hover cursor in the DataTable.

        Returns:
            Lines for fixed cells, and Lines for scrollable cells.
        """
        cursor_type = self.cursor_type
        show_cursor = self.show_cursor
        cache_key = (
            row_index,
            line_no,
            base_style,
            cursor_location,
            hover_location,
            cursor_type,
            show_cursor,
            self._show_hover_cursor,
        )

        if cache_key in self._row_render_cache:
            return self._row_render_cache[cache_key]

        render_cell = self._render_cell

        def _should_highlight(
            cursor_location: Coordinate,
            cell_location: Coordinate,
            cursor_type: CursorType,
        ) -> bool:
            """Determine whether we should highlight a cell given the location
            of the cursor, the location of the cell, and the type of cursor that
            is currently active."""
            if cursor_type == "cell":
                return cursor_location == cell_location
            elif cursor_type == "row":
                cursor_row, _ = cursor_location
                cell_row, _ = cell_location
                return cursor_row == cell_row
            elif cursor_type == "column":
                _, cursor_column = cursor_location
                _, cell_column = cell_location
                return cursor_column == cell_column
            else:
                return False

        if self.fixed_columns:
            fixed_style = self.get_component_styles("datatable--fixed").rich_style
            fixed_style += Style.from_meta({"fixed": True})
            fixed_row = []
            for column in self.columns[: self.fixed_columns]:
                cell_location = Coordinate(row_index, column.index)
                fixed_cell_lines = render_cell(
                    row_index,
                    column.index,
                    fixed_style,
                    column.render_width,
                    cursor=_should_highlight(
                        cursor_location, cell_location, cursor_type
                    ),
                    hover=_should_highlight(hover_location, cell_location, cursor_type),
                )[line_no]
                fixed_row.append(fixed_cell_lines)
        else:
            fixed_row = []

        if row_index == -1:
            row_style = self.get_component_styles("datatable--header").rich_style
        else:
            if self.zebra_stripes:
                component_row_style = (
                    "datatable--odd-row" if row_index % 2 else "datatable--even-row"
                )
                row_style = self.get_component_styles(component_row_style).rich_style
            else:
                row_style = base_style

        scrollable_row = []
        for column in self.columns:
            cell_location = Coordinate(row_index, column.index)
            cell_lines = render_cell(
                row_index,
                column.index,
                row_style,
                column.render_width,
                cursor=_should_highlight(cursor_location, cell_location, cursor_type),
                hover=_should_highlight(hover_location, cell_location, cursor_type),
            )[line_no]
            scrollable_row.append(cell_lines)

        row_pair = (fixed_row, scrollable_row)
        self._row_render_cache[cache_key] = row_pair
        return row_pair

    def _get_offsets(self, y: int) -> tuple[int, int]:
        """Get row number and line offset for a given line.

        Args:
            y: Y coordinate relative to screen top.

        Returns:
            Line number and line offset within cell.
        """
        if self.show_header:
            if y < self.header_height:
                return (-1, y)
            y -= self.header_height
        if y > len(self._y_offsets):
            raise LookupError("Y coord {y!r} is greater than total height")
        return self._y_offsets[y]

    def _render_line(self, y: int, x1: int, x2: int, base_style: Style) -> Strip:
        """Render a line in to a list of segments.

        Args:
            y: Y coordinate of line
            x1: X start crop.
            x2: X end crop (exclusive).
            base_style: Style to apply to line.

        Returns:
            List of segments for rendering.
        """

        width = self.size.width

        try:
            row_index, line_no = self._get_offsets(y)
        except LookupError:
            return Strip.blank(width, base_style)

        cache_key = (
            y,
            x1,
            x2,
            width,
            self.cursor_cell,
            self.hover_cell,
            base_style,
            self.cursor_type,
            self._show_hover_cursor,
        )
        if cache_key in self._line_cache:
            return self._line_cache[cache_key]

        fixed, scrollable = self._render_row(
            row_index,
            line_no,
            base_style,
            cursor_location=self.cursor_cell,
            hover_location=self.hover_cell,
        )
        fixed_width = sum(
            column.render_width for column in self.columns[: self.fixed_columns]
        )

        fixed_line: list[Segment] = list(chain.from_iterable(fixed)) if fixed else []
        scrollable_line: list[Segment] = list(chain.from_iterable(scrollable))

        segments = fixed_line + line_crop(scrollable_line, x1 + fixed_width, x2, width)
        strip = Strip(segments).adjust_cell_length(width, base_style).simplify()

        self._line_cache[cache_key] = strip
        return strip

    def render_line(self, y: int) -> Strip:
        width, height = self.size
        scroll_x, scroll_y = self.scroll_offset
        fixed_top_row_count = sum(
            self.get_row_height(row_index) for row_index in range(self.fixed_rows)
        )
        if self.show_header:
            fixed_top_row_count += self.get_row_height(-1)

        if y >= fixed_top_row_count:
            y += scroll_y

        return self._render_line(y, scroll_x, scroll_x + width, self.rich_style)

    def on_mouse_move(self, event: events.MouseMove):
        self._set_hover_cursor(True)
        meta = event.style.meta
        if meta and self.show_cursor and self.cursor_type != "none":
            try:
                self.hover_cell = Coordinate(meta["row"], meta["column"])
            except KeyError:
                pass

    def _get_fixed_offset(self) -> Spacing:
        top = self.header_height if self.show_header else 0
        top += sum(
            self.rows[row_index].height
            for row_index in range(self.fixed_rows)
            if row_index in self.rows
        )
        left = sum(column.render_width for column in self.columns[: self.fixed_columns])
        return Spacing(top, 0, 0, left)

    def _scroll_cursor_into_view(self, animate: bool = False) -> None:
        fixed_offset = self._get_fixed_offset()
        top, _, _, left = fixed_offset

        if self.cursor_type == "row":
            x, y, width, height = self._get_row_region(self.cursor_row)
            region = Region(int(self.scroll_x) + left, y, width - left, height)
        elif self.cursor_type == "column":
            x, y, width, height = self._get_column_region(self.cursor_column)
            region = Region(x, int(self.scroll_y) + top, width, height - top)
        else:
            region = self._get_cell_region(self.cursor_row, self.cursor_column)

        self.scroll_to_region(region, animate=animate, spacing=fixed_offset)

    def _set_hover_cursor(self, active: bool) -> None:
        """Set whether the hover cursor (the faint cursor you see when you
        hover the mouse cursor over a cell) is visible or not. Typically,
        when you interact with the keyboard, you want to switch the hover
        cursor off.

        Args:
            active: Display the hover cursor.
        """
        self._show_hover_cursor = active
        cursor_type = self.cursor_type
        if cursor_type == "column":
            self.refresh_column(self.hover_column)
        elif cursor_type == "row":
            self.refresh_row(self.hover_row)
        elif cursor_type == "cell":
            self.refresh_cell(*self.hover_cell)

    def on_click(self, event: events.Click) -> None:
        self._set_hover_cursor(True)
        if self.show_cursor and self.cursor_type != "none":
            # Only emit selection events if there is a visible row/col/cell cursor.
            self._emit_selected_message()
            meta = self.get_style_at(event.x, event.y).meta
            if meta:
                self.cursor_cell = Coordinate(meta["row"], meta["column"])
                self._scroll_cursor_into_view(animate=True)
                event.stop()

    def action_cursor_up(self) -> None:
        self._set_hover_cursor(False)
        cursor_type = self.cursor_type
        if self.show_cursor and (cursor_type == "cell" or cursor_type == "row"):
            self.cursor_cell = self.cursor_cell.up()
            self._scroll_cursor_into_view()
        else:
            # If the cursor doesn't move up (e.g. column cursor can't go up),
            # then ensure that we instead scroll the DataTable.
            super().action_scroll_up()

    def action_cursor_down(self) -> None:
        self._set_hover_cursor(False)
        cursor_type = self.cursor_type
        if self.show_cursor and (cursor_type == "cell" or cursor_type == "row"):
            self.cursor_cell = self.cursor_cell.down()
            self._scroll_cursor_into_view()
        else:
            super().action_scroll_down()

    def action_cursor_right(self) -> None:
        self._set_hover_cursor(False)
        cursor_type = self.cursor_type
        if self.show_cursor and (cursor_type == "cell" or cursor_type == "column"):
            self.cursor_cell = self.cursor_cell.right()
            self._scroll_cursor_into_view(animate=True)
        else:
            super().action_scroll_right()

    def action_cursor_left(self) -> None:
        self._set_hover_cursor(False)
        cursor_type = self.cursor_type
        if self.show_cursor and (cursor_type == "cell" or cursor_type == "column"):
            self.cursor_cell = self.cursor_cell.left()
            self._scroll_cursor_into_view(animate=True)
        else:
            super().action_scroll_left()

    def action_select_cursor(self) -> None:
        self._set_hover_cursor(False)
        if self.show_cursor and self.cursor_type != "none":
            self._emit_selected_message()

    def _emit_selected_message(self):
        """Emit the appropriate message for a selection based on the `cursor_type`."""
        cursor_cell = self.cursor_cell
        cursor_type = self.cursor_type
        if cursor_type == "cell":
            self.emit_no_wait(
                DataTable.CellSelected(
                    self,
                    self.get_cell_value(cursor_cell),
                    cursor_cell,
                )
            )
        elif cursor_type == "row":
            row, _ = cursor_cell
            self.emit_no_wait(DataTable.RowSelected(self, row))
        elif cursor_type == "column":
            _, column = cursor_cell
            self.emit_no_wait(DataTable.ColumnSelected(self, column))

    class CellHighlighted(Message, bubble=True):
        """Emitted when the cursor moves to highlight a new cell.
        It's only relevant when the `cursor_type` is `"cell"`.
        It's also emitted when the cell cursor is re-enabled (by setting `show_cursor=True`),
        and when the cursor type is changed to `"cell"`. Can be handled using
        `on_data_table_cell_highlighted` in a subclass of `DataTable` or in a parent
        widget in the DOM.

        Attributes:
            value: The value in the highlighted cell.
            coordinate: The coordinate of the highlighted cell.
        """

        def __init__(
            self, sender: DataTable, value: CellType, coordinate: Coordinate
        ) -> None:
            self.value: CellType = value
            self.coordinate: Coordinate = coordinate
            super().__init__(sender)

        def __rich_repr__(self) -> rich.repr.Result:
            yield "sender", self.sender
            yield "value", self.value
            yield "coordinate", self.coordinate

    class CellSelected(Message, bubble=True):
        """Emitted by the `DataTable` widget when a cell is selected.
        It's only relevant when the `cursor_type` is `"cell"`. Can be handled using
        `on_data_table_cell_selected` in a subclass of `DataTable` or in a parent
        widget in the DOM.

        Attributes:
            value: The value in the cell that was selected.
            coordinate: The coordinate of the cell that was selected.
        """

        def __init__(
            self, sender: DataTable, value: CellType, coordinate: Coordinate
        ) -> None:
            self.value: CellType = value
            self.coordinate: Coordinate = coordinate
            super().__init__(sender)

        def __rich_repr__(self) -> rich.repr.Result:
            yield "sender", self.sender
            yield "value", self.value
            yield "coordinate", self.coordinate

    class RowHighlighted(Message, bubble=True):
        """Emitted when a row is highlighted. This message is only emitted when the
        `cursor_type` is set to `"row"`. Can be handled using `on_data_table_row_highlighted`
        in a subclass of `DataTable` or in a parent widget in the DOM.

        Attributes:
            cursor_row: The y-coordinate of the cursor that highlighted the row.
        """

        def __init__(self, sender: DataTable, cursor_row: int) -> None:
            self.cursor_row: int = cursor_row
            super().__init__(sender)

        def __rich_repr__(self) -> rich.repr.Result:
            yield "sender", self.sender
            yield "cursor_row", self.cursor_row

    class RowSelected(Message, bubble=True):
        """Emitted when a row is selected. This message is only emitted when the
        `cursor_type` is set to `"row"`. Can be handled using
        `on_data_table_row_selected` in a subclass of `DataTable` or in a parent
        widget in the DOM.

        Attributes:
            cursor_row: The y-coordinate of the cursor that made the selection.
        """

        def __init__(self, sender: DataTable, cursor_row: int) -> None:
            self.cursor_row: int = cursor_row
            super().__init__(sender)

        def __rich_repr__(self) -> rich.repr.Result:
            yield "sender", self.sender
            yield "cursor_row", self.cursor_row

    class ColumnHighlighted(Message, bubble=True):
        """Emitted when a column is highlighted. This message is only emitted when the
        `cursor_type` is set to `"column"`. Can be handled using
        `on_data_table_column_highlighted` in a subclass of `DataTable` or in a parent
        widget in the DOM.

        Attributes:
            cursor_column: The x-coordinate of the column that was highlighted.
        """

        def __init__(self, sender: DataTable, cursor_column: int) -> None:
            self.cursor_column: int = cursor_column
            super().__init__(sender)

        def __rich_repr__(self) -> rich.repr.Result:
            yield "sender", self.sender
            yield "cursor_column", self.cursor_column

    class ColumnSelected(Message, bubble=True):
        """Emitted when a column is selected. This message is only emitted when the
        `cursor_type` is set to `"column"`. Can be handled using
        `on_data_table_column_selected` in a subclass of `DataTable` or in a parent
        widget in the DOM.

        Attributes:
            cursor_column: The x-coordinate of the column that was selected.
        """

        def __init__(self, sender: DataTable, cursor_column: int) -> None:
            self.cursor_column: int = cursor_column
            super().__init__(sender)

        def __rich_repr__(self) -> rich.repr.Result:
            yield "sender", self.sender
            yield "cursor_column", self.cursor_column
