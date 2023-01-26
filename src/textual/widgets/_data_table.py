from __future__ import annotations

import functools
from dataclasses import dataclass, field
from itertools import chain, zip_longest
from typing import ClassVar, Generic, Iterable, TypeVar, cast, NamedTuple, Callable

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
from .._two_way_dict import TwoWayDict
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


@functools.total_ordering
class StringKey:
    value: str | None

    def __init__(self, value: str | None = None):
        self.value = value

    def __hash__(self):
        # If a string is supplied, we use the hash of the string. If no string was
        # supplied, we use the default hash to ensure uniqueness amongst instances.
        return hash(self.value) if self.value is not None else id(self)

    def __eq__(self, other: object) -> bool:
        # Strings will match Keys containing the same string value.
        # Otherwise, you'll need to supply the exact same key object.
        return hash(self) == hash(other)

    def __lt__(self, other):
        if isinstance(other, str):
            return self.value < other
        return self.value < other.value


class RowKey(StringKey):
    pass


class ColumnKey(StringKey):
    pass


class CellKey(NamedTuple):
    row_key: RowKey
    column_key: ColumnKey


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

    key: ColumnKey
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

    key: RowKey
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

        self.columns: dict[ColumnKey, Column] = {}
        self.rows: dict[RowKey, Row] = {}
        self.data: dict[RowKey, dict[ColumnKey, CellType]] = {}

        # Keep tracking of key -> index for rows/cols.
        # For a given key, what is the current location of the corresponding row/col?
        self._column_locations: TwoWayDict[ColumnKey, int] = TwoWayDict({})
        self._row_locations: TwoWayDict[RowKey, int] = TwoWayDict({})

        # Maps y-coordinate (from top of table) to (row_index, y-coord within row) pairs
        # self._y_offsets: list[tuple[RowKey, int]] = []
        self._row_render_cache: LRUCache[
            tuple[RowKey, int, Style, int, int], tuple[SegmentLines, SegmentLines]
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

        # TODO: Check what this is used for and if it needs updated to use keys
        self._new_rows: set[int] = set()

        self.show_header = show_header
        self.fixed_rows = fixed_rows
        self.fixed_columns = fixed_columns
        self.zebra_stripes = zebra_stripes
        self.header_height = header_height
        self.show_cursor = show_cursor
        self._show_hover_cursor = False
        self._update_count = 0

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

    @property
    def row_count(self) -> int:
        return len(self.rows)

    @property
    def _y_offsets(self) -> list[tuple[RowKey, int]]:
        y_offsets: list[tuple[RowKey, int]] = []
        for row in self._ordered_rows:
            row_key = row.key
            row_height = row.height
            y_offsets += [(row_key, y) for y in range(row_height)]
        return y_offsets

    def update_cell(
        self, row_key: RowKey | str, column_key: ColumnKey | str, value: CellType
    ) -> None:
        self.data[row_key][column_key] = value
        self._update_count += 1

        row_index = self._row_locations.get(row_key)
        column_index = self._column_locations.get(column_key)
        self.refresh_cell(row_index, column_index)

    def update_coordinate(self, coordinate: Coordinate, value: CellType) -> None:
        row, column = coordinate
        row_key = self._row_locations.get_key(row)
        column_key = self._column_locations.get_key(column)
        self.data[row_key][column_key] = value
        self._update_count += 1
        self.refresh_cell(row, column)

    def get_cell_value(self, coordinate: Coordinate) -> CellType:
        """Get the value from the cell at the given coordinate.

        Args:
            coordinate: The coordinate to retrieve the value from.

        Returns:
            The value of the cell.

        Raises:
            CellDoesNotExist: If there is no cell with the given coordinate.
        """
        # TODO: Rename to get_value_at()?
        #  We need to clearly distinguish between coordinates and cell keys
        row_index, column_index = coordinate
        row_key = self._row_locations.get_key(row_index)
        column_key = self._column_locations.get_key(column_index)
        try:
            cell_value = self.data[row_key][column_key]
        except KeyError:
            raise CellDoesNotExist(f"No cell exists at {coordinate!r}") from None
        return cell_value

    def _clear_caches(self) -> None:
        self._row_render_cache.clear()
        self._cell_render_cache.clear()
        self._line_cache.clear()
        self._styles_cache.clear()

    def get_row_height(self, row_key: int | RowKey) -> int:
        # TODO: Update to generate header key ourselves instead of -1,
        #  and remember to update type signature
        if row_key == -1:
            return self.header_height
        return self.rows[row_key].height

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
        is_valid_row = row_index < len(self.data)
        if is_valid_row:
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
                self._ordered_columns, self._get_row_renderables(row_index)
            ):
                content_width = measure(self.app.console, renderable, 1)
                column.content_width = max(column.content_width, content_width)

        self._clear_caches()
        total_width = sum(column.render_width for column in self.columns.values())
        header_height = self.header_height if self.show_header else 0
        self.virtual_size = Size(
            total_width,
            len(self._y_offsets) + header_height,
        )

    def _get_cell_region(self, row_index: int, column_index: int) -> Region:
        """Get the region of the cell at the given spatial coordinate."""
        valid_row = 0 <= row_index < len(self.rows)
        valid_column = 0 <= column_index < len(self.columns)
        valid_cell = valid_row and valid_column
        if not valid_cell:
            return Region(0, 0, 0, 0)

        row_key = self._row_locations.get_key(row_index)
        row = self.rows[row_key]

        # The x-coordinate of a cell is the sum of widths of cells to the left.
        x = sum(column.render_width for column in self._ordered_columns[:column_index])
        column_key = self._column_locations.get_key(column_index)
        width = self.columns[column_key].render_width
        height = row.height
        y = row.y  # TODO: This value cannot be trusted since we can sort the rows
        if self.show_header:
            y += self.header_height
        cell_region = Region(x, y, width, height)
        return cell_region

    def _get_row_region(self, row_index: int) -> Region:
        """Get the region of the row at the given index."""
        rows = self.rows
        valid_row = 0 <= row_index < len(rows)
        if not valid_row:
            return Region(0, 0, 0, 0)

        row_key = self._row_locations.get_key(row_index)
        row = rows[row_key]
        row_width = sum(column.render_width for column in self.columns.values())
        y = row.y  # TODO: This value cannot be trusted since we can sort the rows
        if self.show_header:
            y += self.header_height
        row_region = Region(0, y, row_width, row.height)
        return row_region

    def _get_column_region(self, column_index: int) -> Region:
        """Get the region of the column at the given index."""
        columns = self.columns
        valid_column = 0 <= column_index < len(columns)
        if not valid_column:
            return Region(0, 0, 0, 0)

        x = sum(column.render_width for column in self._ordered_columns[:column_index])
        column_key = self._column_locations.get_key(column_index)
        width = columns[column_key].render_width
        header_height = self.header_height if self.show_header else 0
        height = len(self._y_offsets) + header_height
        full_column_region = Region(x, 0, width, height)
        return full_column_region

    def clear(self, columns: bool = False) -> None:
        """Clear the table.

        Args:
            columns: Also clear the columns. Defaults to False.
        """
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

    def add_column(
        self, label: TextType, *, width: int | None = None, key: str | None = None
    ) -> ColumnKey:
        """Add a column to the table.

        Args:
            label: A str or Text object containing the label (shown top of column).
            width: Width of the column in cells or None to fit content. Defaults to None.
            key: A key which uniquely identifies this column. If None, it will be generated for you. Defaults to None.

        Returns:
            Uniquely identifies this column. Can be used to retrieve this column regardless
                of its current location in the DataTable (it could have moved after being added
                due to sorting or insertion/deletion of other columns).
        """
        text_label = Text.from_markup(label) if isinstance(label, str) else label

        column_key = ColumnKey(key)
        column_index = len(self.columns)
        content_width = measure(self.app.console, text_label, 1)
        if width is None:
            column = Column(
                column_key,
                text_label,
                content_width,
                index=column_index,
                content_width=content_width,
                auto_width=True,
            )
        else:
            column = Column(
                column_key,
                text_label,
                width,
                content_width=content_width,
                index=column_index,
            )

        self.columns[column_key] = column
        self._column_locations[column_key] = column_index
        self._require_update_dimensions = True
        self.check_idle()

        return column_key

    def add_row(
        self, *cells: CellType, height: int = 1, key: str | None = None
    ) -> RowKey:
        """Add a row at the bottom of the DataTable.

        Args:
            *cells: Positional arguments should contain cell data.
            height: The height of a row (in lines). Defaults to 1.
            key: A key which uniquely identifies this row. If None, it will be generated for you. Defaults to None.

        Returns:
            Uniquely identifies this row. Can be used to retrieve this row regardless
                of its current location in the DataTable (it could have moved after being added
                due to sorting or insertion/deletion of other rows).
        """
        row_index = self.row_count
        row_key = RowKey(key)

        # TODO: If there are no columns, do we generate them here?
        #  If we don't do this, users will be required to call add_column(s)
        #  Before they call add_row.

        # Map the key of this row to its current index
        self._row_locations[row_key] = row_index
        self.data[row_key] = {
            column.key: cell
            for column, cell in zip_longest(self._ordered_columns, cells)
        }
        self.rows[row_key] = Row(row_key, row_index, height, self._line_no)

        # for line_no in range(height):
        #     self._y_offsets.append((row_key, line_no))

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

        return row_key

    def add_columns(self, *labels: TextType) -> list[ColumnKey]:
        """Add a number of columns.

        Args:
            *labels: Column headers.

        Returns:
            A list of the keys for the columns that were added. See
            the `add_column` method docstring for more information on how
            these keys are used.
        """
        column_keys = []
        for label in labels:
            column_key = self.add_column(label, width=None)
            column_keys.append(column_key)
        return column_keys

    def add_rows(self, rows: Iterable[Iterable[CellType]]) -> list[RowKey]:
        """Add a number of rows at the bottom of the DataTable.

        Args:
            rows: Iterable of rows. A row is an iterable of cells.

        Returns:
            A list of the keys for the rows that were added. See
            the `add_row` method docstring for more information on how
            these keys are used.
        """
        row_keys = []
        for row in rows:
            row_key = self.add_row(*row)
            row_keys.append(row_key)
        return row_keys

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

    @property
    def _ordered_columns(self) -> list[Column]:
        column_indices = range(len(self.columns))
        column_keys = [
            self._column_locations.get_key(index) for index in column_indices
        ]
        ordered_columns = [self.columns.get(key) for key in column_keys]
        return ordered_columns

    @property
    def _ordered_rows(self) -> list[Row]:
        row_indices = range(self.row_count)
        ordered_rows = []
        for row_index in row_indices:
            row_key = self._row_locations.get_key(row_index)
            row = self.rows.get(row_key)
            ordered_rows.append(row)
        return ordered_rows

    def _get_row_renderables(self, row_index: int) -> list[RenderableType]:
        """Get renderables for the row currently at the given row index.

        Args:
            row_index: Index of the row.

        Returns:
            List of renderables
        """

        # TODO:  We have quite a few back and forward key/index conversions, could probably reduce them
        ordered_columns = self._ordered_columns
        if row_index == -1:
            row = [column.label for column in ordered_columns]
            return row

        # Ensure we order the cells in the row based on current column ordering
        row_key = self._row_locations.get_key(row_index)
        cell_mapping: dict[ColumnKey, CellType] = self.data.get(row_key)
        print(row_index, cell_mapping.values())

        ordered_row: list[CellType] = []
        for column in ordered_columns:
            cell = cell_mapping[column.key]
            ordered_row.append(cell)

        empty = Text()
        if ordered_row is None:
            return [empty for _ in self.columns]
        else:
            return [
                Text() if datum is None else default_cell_formatter(datum) or empty
                for datum, _ in zip_longest(ordered_row, range(len(self.columns)))
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
                # Apply subtle variation in style for the fixed (blue background by
                # default) rows and columns affected by the cursor, to ensure we can
                # still differentiate between the labels and the data.
                style += self.get_component_styles(
                    "datatable--highlight-fixed"
                ).rich_style

        if cursor and show_cursor:
            style += self.get_component_styles("datatable--cursor").rich_style
            if is_fixed_style:
                style += self.get_component_styles("datatable--cursor-fixed").rich_style

        # TODO: We can hoist `row_key` lookup waaay up to do it inside `_get_offsets`
        #  then just pass it through to here instead of the row_index.
        row_key = self._row_locations.get_key(row_index)
        column_key = self._column_locations.get_key(column_index)
        cell_cache_key = (row_key, column_key, style, cursor, hover, self._update_count)
        if cell_cache_key not in self._cell_render_cache:
            if not is_header_row:
                style += Style.from_meta({"row": row_index, "column": column_index})
            height = self.header_height if is_header_row else self.rows[row_key].height
            cell = self._get_row_renderables(row_index)[column_index]
            print(f"CELL = {cell}")
            lines = self.app.console.render_lines(
                Padding(cell, (0, 1)),
                self.app.console.options.update_dimensions(width, height),
                style=style,
            )
            self._cell_render_cache[cell_cache_key] = lines
        return self._cell_render_cache[cell_cache_key]

    def _render_line_in_row(
        self,
        row_key: RowKey,
        line_no: int,
        base_style: Style,
        cursor_location: Coordinate,
        hover_location: Coordinate,
    ) -> tuple[SegmentLines, SegmentLines]:
        """Render a row in to lines for each cell.

        Args:
            row_key: The identifying key for this row.
            line_no: Line number (y-coordinate) within row. 0 is the first strip of
                cells in the row, line_no=1 is the next, and so on...
            base_style: Base style of row.
            cursor_location: The location of the cursor in the DataTable.
            hover_location: The location of the hover cursor in the DataTable.

        Returns:
            Lines for fixed cells, and Lines for scrollable cells.
        """
        cursor_type = self.cursor_type
        show_cursor = self.show_cursor

        cache_key = (
            row_key,
            line_no,
            base_style,
            cursor_location,
            hover_location,
            cursor_type,
            show_cursor,
            self._show_hover_cursor,
            self._update_count,
        )

        if cache_key in self._row_render_cache:
            return self._row_render_cache[cache_key]

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

        row_index = self._row_locations.get(row_key, -1)
        render_cell = self._render_cell
        if self.fixed_columns:
            fixed_style = self.get_component_styles("datatable--fixed").rich_style
            fixed_style += Style.from_meta({"fixed": True})
            fixed_row = []
            for column_index, column in enumerate(
                self._ordered_columns[: self.fixed_columns]
            ):
                cell_location = Coordinate(row_index, column_index)
                fixed_cell_lines = render_cell(
                    row_index,
                    column_index,
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

        if row_key is None:
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
        for column_index, column in enumerate(self._ordered_columns):
            cell_location = Coordinate(row_index, column_index)
            cell_lines = render_cell(
                row_index,
                column_index,
                row_style,
                column.render_width,
                cursor=_should_highlight(cursor_location, cell_location, cursor_type),
                hover=_should_highlight(hover_location, cell_location, cursor_type),
            )[line_no]
            scrollable_row.append(cell_lines)

        row_pair = (fixed_row, scrollable_row)
        self._row_render_cache[cache_key] = row_pair
        return row_pair

    def _get_offsets(self, y: int) -> tuple[RowKey | None, int]:
        """Get row key and line offset for a given line.

        Args:
            y: Y coordinate relative to DataTable top.

        Returns:
            Row key and line (y) offset within cell.
        """

        # TODO - the row sorting issue is here, since when we sort rows we never update the
        #  y-offsets - lets make those offsets dynamic.

        header_height = self.header_height
        y_offsets = self._y_offsets
        if self.show_header:
            if y < header_height:
                return None, y
            y -= header_height
        if y > len(y_offsets):
            raise LookupError("Y coord {y!r} is greater than total height")

        return y_offsets[y]

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
            row_key, y_offset_in_row = self._get_offsets(y)
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
            self._update_count,
        )
        if cache_key in self._line_cache:
            return self._line_cache[cache_key]

        fixed, scrollable = self._render_line_in_row(
            row_key,
            y_offset_in_row,
            base_style,
            cursor_location=self.cursor_cell,
            hover_location=self.hover_cell,
        )
        fixed_width = sum(
            column.render_width
            for column in self._ordered_columns[: self.fixed_columns]
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

        fixed_row_keys: list[RowKey] = [
            self._row_locations.get_key(row_index)
            for row_index in range(self.fixed_rows)
        ]

        fixed_rows_height = sum(
            self.get_row_height(row_key) for row_key in fixed_row_keys
        )
        if self.show_header:
            fixed_rows_height += self.get_row_height(-1)

        if y >= fixed_rows_height:
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
            self.rows[self._row_locations.get_key(row_index)].height
            for row_index in range(self.fixed_rows)
            if row_index in self.rows
        )
        left = sum(
            column.render_width
            for column in self._ordered_columns[: self.fixed_columns]
        )
        return Spacing(top, 0, 0, left)

    def sort_columns(
        self, key: Callable[[ColumnKey | str], str] = None, reverse: bool = False
    ) -> None:
        ordered_keys = sorted(self.columns.keys(), key=key, reverse=reverse)
        self._column_locations = TwoWayDict(
            {key: new_index for new_index, key in enumerate(ordered_keys)}
        )
        self._update_count += 1
        self.refresh()

    def sort_rows(
        self, key: Callable[[RowKey | str], str] = None, reverse: bool = False
    ):
        ordered_keys = sorted(self.rows.keys(), key=key, reverse=reverse)
        self._row_locations = TwoWayDict(
            {key: new_index for new_index, key in enumerate(ordered_keys)}
        )
        self._update_count += 1
        self.refresh()

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
