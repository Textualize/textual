from __future__ import annotations

from dataclasses import dataclass, field
from typing import ClassVar, Generic, TypeVar, cast

from rich.console import RenderableType
from rich.padding import Padding
from rich.segment import Segment
from rich.style import Style
from rich.text import Text, TextType

from .._lru_cache import LRUCache
from .._segment_tools import line_crop
from .._types import Lines
from ..geometry import Region, Size
from ..reactive import Reactive
from .._profile import timer
from ..scroll_view import ScrollView
from ..widget import Widget

CellType = TypeVar("CellType")


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

        self._cells: dict[int, list[Cell]] = {}
        self._cell_render_cache: dict[tuple[int, int], Lines] = LRUCache(10000)

    show_header = Reactive(True)
    fixed_rows = Reactive(1)
    fixed_columns = Reactive(1)
    zebra_stripes = Reactive(False)

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
        self.rows[row_index] = Row(
            row_index,
            height=height,
            cell_renderables=[
                Text.from_markup(cell) if isinstance(cell, str) else cell
                for cell in cells
            ],
        )
        self.row_count += 1
        self._update_dimensions()
        self.refresh()

    def get_row(self, y: int) -> list[CellType | Text]:

        if y == 0 and self.show_header:
            row = [column.label for column in self.columns]
            return row

        data_offset = y - 1 if self.show_header else 0
        data = self.data.get(data_offset)
        if data is None:
            return [Text() for column in self.columns]
        else:
            return self.rows[data_offset].cell_renderables

    def _render_cell(self, y: int, column: Column) -> Lines:

        style = Style.from_meta({"y": y, "column": column.index})

        cell_key = (y, column.index)
        if cell_key not in self._cell_render_cache:
            cell = self.get_row(y)[column.index]
            lines = self.app.console.render_lines(
                Padding(cell, (0, 1)),
                self.app.console.options.update_dimensions(column.width, 1),
                style=style,
            )
            self._cell_render_cache[cell_key] = lines

        return self._cell_render_cache[cell_key]

    def _render_line(self, y: int, x1: int, x2: int) -> list[Segment]:

        width = self.content_region.width

        cell_segments: list[list[Segment]] = []
        rendered_width = 0
        for column in self.columns:
            lines = self._render_cell(y, column)
            rendered_width += column.width
            cell_segments.append(lines[0])

        base_style = self.rich_style

        fixed_style = self.component_styles[
            "datatable--fixed"
        ].node.rich_style + Style.from_meta({"fixed": True})
        header_style = self.component_styles[
            "datatable--header"
        ].node.rich_style + Style.from_meta({"header": True})

        fixed: list[Segment] = sum(cell_segments[: self.fixed_columns], start=[])
        fixed_width = sum(column.width for column in self.columns[: self.fixed_columns])

        fixed = list(Segment.apply_style(fixed, fixed_style))

        line: list[Segment] = sum(cell_segments, start=[])

        row_style = base_style
        if y == 0:
            segments = fixed + line_crop(line, x1 + fixed_width, x2, width)
            line = Segment.adjust_line_length(segments, width)
        else:
            if self.zebra_stripes:
                component_row_style = (
                    "datatable--odd-row" if y % 2 else "datatable--even-row"
                )
                row_style = self.component_styles[component_row_style].node.rich_style

            line = list(Segment.apply_style(line, row_style))
            segments = fixed + line_crop(line, x1 + fixed_width, x2, width)
            line = Segment.adjust_line_length(segments, width, style=base_style)

        if y == 0 and self.show_header:
            line = list(Segment.apply_style(line, header_style))

        return line

    @timer("render_lines")
    def render_lines(self, crop: Region) -> Lines:

        scroll_x, scroll_y = self.scroll_offset
        x1, y1, x2, y2 = crop.translate(scroll_x, scroll_y).corners

        fixed_lines = [self._render_line(y, x1, x2) for y in range(0, self.fixed_rows)]
        lines = [self._render_line(y, x1, x2) for y in range(y1, y2)]

        for fixed_line, y in zip(fixed_lines, range(y1, y2)):
            if y - scroll_y == 0:
                lines[0] = fixed_line

        return lines

    def on_mouse_move(self, event):
        print(self.get_style_at(event.x, event.y).meta)
