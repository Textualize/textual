from __future__ import annotations

from dataclasses import dataclass, field
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

CellFormatter = Callable[[object], RenderableType | None]


def default_cell_formatter(obj: object) -> RenderableType | None:
    if isinstance(obj, str):
        return Text.from_markup(obj)
    if not is_renderable(obj):
        raise TypeError("Table cell contains {obj!r} which is not renderable")
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
    height: int = 1
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

        self.line_contents: list[str] = []

        self._row_render_cache: LRUCache[int, tuple[Lines, Lines]] = LRUCache(1000)
        self._cell_render_cache: LRUCache[tuple[int, int, Style], Lines] = LRUCache(
            10000
        )
        self._line_cache: LRUCache[tuple[int, int, int, int], list[Segment]] = LRUCache(
            1000
        )

    show_header = Reactive(True)
    fixed_rows = Reactive(1)
    fixed_columns = Reactive(1)
    zebra_stripes = Reactive(False)

    def _clear_caches(self) -> None:
        self._row_render_cache.clear()
        self._cell_render_cache.clear()
        self._line_cache.clear()

    async def handle_styles_updated(self, message: messages.StylesUpdated) -> None:
        self._clear_caches()

    def watch_show_header(self, show_header: bool) -> None:
        self._clear_caches()

    def watch_fixed_rows(self, fixed_rows: int) -> None:
        self._clear_caches()

    def watch_zebra_stripes(self, zebra_stripes: int) -> None:
        self._clear_caches()

    def _update_dimensions(self) -> None:
        max_width = sum(column.width for column in self.columns)
        self.virtual_size = Size(max_width, len(self.data) + self.show_header)

    def add_column(self, label: TextType, *, width: int = 10) -> None:
        text_label = Text.from_markup(label) if isinstance(label, str) else label
        self.columns.append(Column(text_label, width, index=len(self.columns)))
        self._update_dimensions()
        self.refresh()

    def add_row(self, *cells: CellType, height: int = 1) -> None:
        row_index = self.row_count
        self.data[row_index] = list(cells)
        self.rows[row_index] = Row(row_index, height=height)
        self.row_count += 1
        self._update_dimensions()
        self.refresh()

    def get_row(self, row_index: int) -> list[RenderableType]:

        if row_index == 0 and self.show_header:
            row = [column.label for column in self.columns]
            return row

        data_offset = row_index - 1 if self.show_header else 0
        data = self.data.get(data_offset)
        empty = Text()
        if data is None:
            return [empty for column in self.columns]
        else:
            return [default_cell_formatter(datum) or empty for datum in data]

    def _render_cell(self, row_index: int, column: Column, style: Style) -> Lines:

        cell_key = (row_index, column.index, style)
        if cell_key not in self._cell_render_cache:
            style += Style.from_meta({"row": row_index, "column": column.index})
            cell = self.get_row(row_index)[column.index]
            lines = self.app.console.render_lines(
                Padding(cell, (0, 1)),
                self.app.console.options.update_dimensions(column.width, 1),
                style=style,
            )
            self._cell_render_cache[cell_key] = lines
        return self._cell_render_cache[cell_key]

    def _render_row(self, row_index: int, base_style: Style) -> tuple[Lines, Lines]:
        if row_index in self._row_render_cache:
            return self._row_render_cache[row_index]

        if self.fixed_columns:
            fixed_style = self.component_styles["datatable--fixed"].node.rich_style
            fixed_style += Style.from_meta({"fixed": True})

            fixed_row = [
                self._render_cell(row_index, column, fixed_style)[0]
                for column in self.columns[: self.fixed_columns]
            ]
        else:
            fixed_row = []

        if row_index == 0 and self.show_header:
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
            self._render_cell(row_index, column, row_style)[0]
            for column in self.columns
        ]

        row_pair = (fixed_row, scrollable_row)
        self._row_render_cache[row_index] = row_pair
        return row_pair

    def _render_line(
        self, y: int, x1: int, x2: int, base_style: Style
    ) -> list[Segment]:

        width = self.content_region.width

        cache_key = (y, x1, x2, width)
        if cache_key in self._line_cache:
            return self._line_cache[cache_key]

        row_index = y

        fixed, scrollable = self._render_row(row_index, base_style)
        fixed_width = sum(column.width for column in self.columns[: self.fixed_columns])

        fixed_line: list[Segment] = sum(fixed, start=[])
        scrollable_line: list[Segment] = sum(scrollable, start=[])

        segments = fixed_line + line_crop(scrollable_line, x1 + fixed_width, x2, width)

        # line = Segment.adjust_line_length(segments, width, style=base_style)
        remaining_width = width - (fixed_width + min(width, (x2 - x1 + fixed_width)))
        if remaining_width > 0:
            segments.append(Segment(" " * remaining_width, base_style))
        elif remaining_width < 0:
            segments = Segment.adjust_line_length(segments, width, style=base_style)

        self._line_cache[cache_key] = segments
        return segments

    @timer("render_lines")
    def render_lines(self, crop: Region) -> Lines:

        scroll_x, scroll_y = self.scroll_offset
        x1, y1, x2, y2 = crop.translate(scroll_x, scroll_y).corners

        base_style = self.rich_style

        fixed_lines = [
            self._render_line(y, x1, x2, base_style) for y in range(0, self.fixed_rows)
        ]
        lines = [self._render_line(y, x1, x2, base_style) for y in range(y1, y2)]

        for fixed_line, y in zip(fixed_lines, range(y1, y2)):
            if y - scroll_y == 0:
                lines[0] = fixed_line

        return lines

    def on_mouse_move(self, event):
        print(self.get_style_at(event.x, event.y).meta)
