from __future__ import annotations

from dataclasses import dataclass, field
from itertools import chain
from typing import Callable, ClassVar, Generic, TypeVar, cast

from rich.console import RenderableType
from rich.padding import Padding
from rich.protocol import is_renderable
from rich.segment import Segment
from rich.style import Style
from rich.text import Text, TextType

from .._cache import LRUCache
from .._segment_tools import line_crop
from .._types import Lines
from ..geometry import Region, Size
from ..reactive import Reactive
from .._profile import timer
from ..scroll_view import ScrollView
from ..widget import Widget
from .. import messages

CellType = TypeVar("CellType")


def default_cell_formatter(obj: object) -> RenderableType | None:
    if isinstance(obj, str):
        return Text.from_markup(obj)
    if not is_renderable(obj):
        raise TypeError(f"Table cell {obj!r} is not renderable")
    return cast(RenderableType, obj)


@dataclass
class Column:
    label: Text
    width: int
    visible: bool = False
    index: int = 0


@dataclass
class Row:
    index: int
    height: int
    cell_renderables: list[RenderableType] = field(default_factory=list)


@dataclass
class Cell:
    value: object


class Header(Widget):
    pass


class DataTable(ScrollView, Generic[CellType]):

    CSS = """
    DataTable {
        background: $surface;
        color: $text-surface;       
    }
    DataTable > .datatable--header {        
        text-style: bold;
        background: $primary;
        color: $text-primary;
    }
    DataTable > .datatable--fixed {
        text-style: bold;
        background: $primary-darken-2;
        color: $text-primary-darken-2;
    }

    DataTable > .datatable--odd-row {
        
    }

    DataTable > .datatable--even-row {
        background: $primary 10%;
    }

    .-dark-mode DataTable > .datatable--even-row {
        background: $primary 15%;
    }

    DataTable > .datatable--highlight {
        background: $secondary;
        color: $text-secondary;
    }
    """

    COMPONENT_CLASSES: ClassVar[set[str]] = {
        "datatable--header",
        "datatable--fixed",
        "datatable--odd-row",
        "datatable--even-row",
        "datatable--highlight",
    }

    def __init__(
        self,
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

        self._row_render_cache: LRUCache[tuple[int, int, Style], tuple[Lines, Lines]]
        self._row_render_cache = LRUCache(1000)

        self._cell_render_cache: LRUCache[tuple[int, int, Style], Lines]
        self._cell_render_cache = LRUCache(10000)

        self._line_cache: LRUCache[tuple[int, int, int, int], list[Segment]]
        self._line_cache = LRUCache(1000)

    show_header = Reactive(True)
    fixed_rows = Reactive(0)
    fixed_columns = Reactive(1)
    zebra_stripes = Reactive(False)
    header_height = Reactive(1)

    def _clear_caches(self) -> None:
        self._row_render_cache.clear()
        self._cell_render_cache.clear()
        self._line_cache.clear()

    def get_row_height(self, row_index: int) -> int:
        if row_index == -1:
            return self.header_height
        return self.rows[row_index].height

    async def handle_styles_updated(self, message: messages.StylesUpdated) -> None:
        self._clear_caches()

    def watch_show_header(self, show_header: bool) -> None:
        self._clear_caches()

    def watch_fixed_rows(self, fixed_rows: int) -> None:
        self._clear_caches()

    def watch_zebra_stripes(self, zebra_stripes: bool) -> None:
        self._clear_caches()

    def _update_dimensions(self) -> None:
        """Called to recalculate the virtual (scrollable) size."""
        total_width = sum(column.width for column in self.columns)
        self.virtual_size = Size(
            total_width,
            len(self._y_offsets) + (self.header_height if self.show_header else 0),
        )

    def add_column(self, label: TextType, *, width: int = 10) -> None:
        """Add a column to the table.

        Args:
            label (TextType): A str or Text object containing the label (shown top of column)
            width (int, optional): Width of the column in cells. Defaults to 10.
        """
        text_label = Text.from_markup(label) if isinstance(label, str) else label
        self.columns.append(Column(text_label, width, index=len(self.columns)))
        self._update_dimensions()
        self.refresh()

    def add_row(self, *cells: CellType, height: int = 1) -> None:
        """Add a row.

        Args:
            height (int, optional): The height of a row (in lines). Defaults to 1.
        """
        row_index = self.row_count
        self.data[row_index] = list(cells)
        self.rows[row_index] = Row(row_index, height=height)

        for line_no in range(height):
            self._y_offsets.append((row_index, line_no))

        self.row_count += 1
        self._update_dimensions()
        self.refresh()

    def _get_row_renderables(self, row_index: int) -> list[RenderableType]:
        """Get renderables for the given row.

        Args:
            row_index (int): Index of the row.

        Returns:
            list[RenderableType]: List of renderables
        """

        if row_index == -1:
            row = [column.label for column in self.columns]
            return row

        data = self.data.get(row_index)
        empty = Text()
        if data is None:
            return [empty for _ in self.columns]
        else:
            return [default_cell_formatter(datum) or empty for datum in data]

    def _render_cell(
        self, row_index: int, column_index: int, style: Style, width: int
    ) -> Lines:
        """Render the given cell.

        Args:
            row_index (int): Index of the row.
            column_index (int): Index of the column.
            style (Style): Style to apply.
            width (int): Width of the cell.

        Returns:
            Lines: A list of segments per line.
        """
        cell_key = (row_index, column_index, style)
        if cell_key not in self._cell_render_cache:
            style += Style.from_meta({"row": row_index, "column": column_index})
            height = (
                self.header_height if row_index == -1 else self.rows[row_index].height
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
        self, row_index: int, line_no: int, base_style: Style
    ) -> tuple[Lines, Lines]:
        """Render a row in to lines for each cell.

        Args:
            row_index (int): Index of the row.
            line_no (int): Line number (on screen, 0 is top)
            base_style (Style): Base style of row.

        Returns:
            tuple[Lines, Lines]: Lines for fixed cells, and Lines for scrollable cells.
        """

        cache_key = (row_index, line_no, base_style)

        if cache_key in self._row_render_cache:
            return self._row_render_cache[cache_key]

        render_cell = self._render_cell

        if self.fixed_columns:
            fixed_style = self.component_styles["datatable--fixed"].node.rich_style
            fixed_style += Style.from_meta({"fixed": True})
            fixed_row = [
                render_cell(row_index, column.index, fixed_style, column.width)[line_no]
                for column in self.columns[: self.fixed_columns]
            ]
        else:
            fixed_row = []

        if row_index == -1:
            row_style = self.component_styles["datatable--header"].node.rich_style
        else:
            if self.zebra_stripes:
                component_row_style = (
                    "datatable--odd-row" if row_index % 2 else "datatable--even-row"
                )
                row_style = self.component_styles[component_row_style].node.rich_style
            else:
                row_style = base_style

        scrollable_row = [
            render_cell(row_index, column.index, row_style, column.width)[line_no]
            for column in self.columns
        ]

        row_pair = (fixed_row, scrollable_row)
        self._row_render_cache[cache_key] = row_pair
        return row_pair

    def _get_offsets(self, y: int) -> tuple[int, int]:
        """Get row number and line offset for a given line.

        Args:
            y (int): Y coordinate relative to screen top.

        Returns:
            tuple[int, int]: Line number and line offset within cell.
        """
        if self.show_header:
            if y < self.header_height:
                return (-1, y)
            y -= self.header_height
        return self._y_offsets[y]

    def _render_line(
        self, y: int, x1: int, x2: int, base_style: Style
    ) -> list[Segment]:
        """Render a line in to a list of segments.

        Args:
            y (int): Y coordinate of line
            x1 (int): X start crop.
            x2 (int): X end crop (exclusive).
            base_style (Style): Style to apply to line.

        Returns:
            list[Segment]: List of segments for rendering.
        """

        width = self.content_region.width

        cache_key = (y, x1, x2, width)
        if cache_key in self._line_cache:
            return self._line_cache[cache_key]

        row_index, line_no = self._get_offsets(y)

        fixed, scrollable = self._render_row(row_index, line_no, base_style)
        fixed_width = sum(column.width for column in self.columns[: self.fixed_columns])

        fixed_line: list[Segment] = list(chain.from_iterable(fixed)) if fixed else []
        scrollable_line: list[Segment] = list(chain.from_iterable(scrollable))

        segments = fixed_line + line_crop(scrollable_line, x1 + fixed_width, x2, width)

        remaining_width = width - (fixed_width + min(width, (x2 - x1 + fixed_width)))
        if remaining_width > 0:
            segments.append(Segment(" " * remaining_width, base_style))
        elif remaining_width < 0:
            segments = Segment.adjust_line_length(segments, width, style=base_style)

        simplified_segments = list(Segment.simplify(segments))

        self._line_cache[cache_key] = simplified_segments
        return segments

    @timer("render_lines")
    def render_lines(self, crop: Region) -> Lines:
        """Render lines within a given region.

        Args:
            crop (Region): Region to crop to.

        Returns:
            Lines: A list of segments for every line within crop region.
        """

        scroll_x, scroll_y = self.scroll_offset
        x1, y1, x2, y2 = crop.translate(scroll_x, scroll_y).corners

        base_style = self.rich_style

        fixed_top_row_count = sum(
            self.get_row_height(row_index) for row_index in range(self.fixed_rows)
        )
        if self.show_header:
            fixed_top_row_count += self.get_row_height(-1)

        render_line = self._render_line
        fixed_lines = [
            render_line(y, x1, x2, base_style) for y in range(0, fixed_top_row_count)
        ]
        lines = [render_line(y, x1, x2, base_style) for y in range(y1, y2)]

        for line_index, y in enumerate(range(y1, y2)):
            if y - scroll_y < fixed_top_row_count:
                lines[line_index] = fixed_lines[line_index]

        return lines

    def on_mouse_move(self, event):
        print(self.get_style_at(event.x, event.y).meta)
