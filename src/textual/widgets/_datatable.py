from __future__ import annotations

from rich.segment import Segment

from typing import cast, Generic, TypeVar

from collections.abc import Container
from dataclasses import dataclass

from rich.console import RenderableType
from rich.text import TextType

from .._lru_cache import LRUCache
from .._types import Lines
from ..scroll_view import ScrollView


RowType = TypeVar("RowType")
IndexType = TypeVar("IndexType", int, str)


@dataclass
class Column(Generic[IndexType]):
    index: IndexType
    label: TextType
    width: int
    visible: bool = False


@dataclass
class Cell:
    value: object


class DataTable(ScrollView, Generic[RowType, IndexType]):
    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.columns: list[Column[IndexType]] = []
        self.rows: dict[int, RowType] = {}
        self.row_count = 0
        self._cells: dict[int, list[Cell]] = {}

        self._cell_render_cache: dict[tuple[int, IndexType, int], Lines] = LRUCache(
            1000
        )

    def add_column(self, label: TextType, index: IndexType | None, width: int) -> None:
        if index is None:
            index = cast(IndexType, len(self.columns))
        self.columns.append(Column(index, label, width))
        self.refresh()

    def add_row(self, row: RowType) -> None:
        self.rows[self.row_count] = row
        self.row_count += 1
        self.refresh()

    def _get_row(self, row_index: int) -> RowType | None:
        return self.rows.get(row_index)

    def _get_cell(self, row_index: int, column: IndexType) -> object | None:
        row = self.rows.get(row_index)
        if row is None:
            return None
        try:
            return row[column]
        except LookupError:
            return None

    # def _render_cell(self, row_index: int, column: IndexType) -> Lines:

    #     cell = self._get_cell(row_index, column)

    # def render_row(
    #     self,
    #     row: int,
    # ):
    #     list[list[Segment]]

    # def _render_cell(self, row: int, column: int) -> Lines:

    #     self.app.console.render_lines()

    def render_lines(self, start: int, end: int) -> Lines:
        pass
