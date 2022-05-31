from __future__ import annotations

from abc import abstractmethod, ABC

from rich.console import Console, ConsoleOptions, RenderResult
from rich.text import Text

from dataclasses import dataclass
from typing import Awaitable, Callable, Generic, TypeVar

from ..geometry import Size
from .._lru_cache import LRUCache
from ..scroll_view import ScrollView


RowType = TypeVar("RowType")

RowSetter = Callable[[RowType | None], Awaitable[None]]


class DataProvider(ABC):
    @abstractmethod
    async def start(self) -> None:
        pass

    @abstractmethod
    async def get_size(self) -> int | None:
        ...

    @abstractmethod
    async def request_row(self, row_no: int, set_row: RowSetter) -> None:
        ...


class DictListProvider:
    def __init__(self, data: list[list]) -> None:
        self.data = data

    async def start(self) -> None:
        pass

    async def get_size(self) -> int | None:
        return len(self.data)

    async def request_row(self, row_no: int, set_row: RowSetter) -> None:
        if row_no > len(self.data):
            await set_row(None)
        else:
            row = self.data[row_no]
            await set_row(row)


@dataclass
class Column:
    label: Text
    width: int


class _TableRenderable:
    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        pass


class DataTable(ScrollView, Generic[RowType]):
    def __init__(
        self,
        data_provider: DataProvider | None,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)

        self._data_provider = data_provider
        self._columns: list[Column]
        self._rows = LRUCache[int, RowType]

        self.height = 0

    def get_content_height(self, container: Size, viewport: Size, width: int) -> int:
        return super().get_content_height(container, viewport, width)

    async def set_row(self, row_no: int, row: RowType):
        pass
