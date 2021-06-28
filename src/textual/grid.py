from __future__ import annotations

from enum import Enum
from dataclasses import dataclass
from typing import Iterable, NamedTuple, Optional, Sequence, Tuple, TYPE_CHECKING, Union

from rich import print
from rich._ratio import ratio_resolve

from .layout import LayoutBase
from .widget import WidgetBase


class Track(NamedTuple):
    """Any object that defines an edge (such as Layout)."""

    size: Optional[int] = None
    ratio: int = 1
    minimum_size: int = 1
    name: str = ""


class Justify(Enum):
    START = 1
    END = 2
    CENTER = 3
    STRETCH = 4


class JustifyContent(Enum):
    START = 1
    END = 2
    CENTER = 3
    STRETCH = 4
    SPACE_AROUND = 5
    SPACE_BETWEEN = 6
    SPACE_EVENLY = 7


ItemArea = Tuple[Union[str, int], Union[str, int], Union[str, int], Union[str, int]]


class Grid(LayoutBase):
    def __init__(
        self,
        verticals: Iterable[Track],
        horizontals: Iterable[Track],
        vertical_gap: int = 0,
        horizontal_gap: int = 0,
        justify_items: Justify = Justify.START,
        align_items: Justify = Justify.START,
        justify_content: JustifyContent = JustifyContent.START,
        align_content: JustifyContent = JustifyContent.START,
        areas: dict[str, ItemArea] | None = None,
    ) -> None:
        self.verticals = list(verticals)
        self.horizontals = list(horizontals)
        self.vertical_gap = vertical_gap
        self.horizontal_gap = horizontal_gap
        self.justify_items = justify_items
        self.align_items = align_items
        self.justify_content = justify_content
        self.align_content = align_content
        self.areas = areas or {}
        super().__init__()

    def add_widget(self, widget: WidgetBase, area: ItemArea) -> None:
        pass

    @classmethod
    def _resolve_tracks(cls, tracks: Sequence[Track], total: int) -> list[int]:

        sizes = ratio_resolve(total, tracks)
        track_sizes = [(track.name, size) for track, size in zip(tracks, sizes)]

        named_tracks: list[tuple[set[str], str, int]] = [
            (set(), "", 0),
            *((set(), name, size) for name, size in track_sizes),
        ]

        for (names1, name1, _size1), (names2, name2, _size2) in zip(
            named_tracks[:], named_tracks[1:]
        ):
            if name1:
                names1.add(f"end-{name1}")
                names1.add(name1)
            if name2:
                names2.add(name2)
                names2.add(f"end-{name2}")
                names1.add(f"start-{name2}")

        result = [(track_set, size) for track_set, _, size in named_tracks]
        print(result)

        return sizes

    def reflow(self, console, width: int, height: int) -> None:
        self.map.clear()

        vertical_sizes = self._resolve_tracks(self.verticals, width)
        horizontal_sizes = self._resolve_tracks(self.horizontals, width)

        # print(vertical_sizes)
        # print(horizontal_sizes)


if __name__ == "__main__":

    grid = Grid(
        verticals=[Track(size=60, name="sidebar"), Track(name="content")],
        horizontals=[
            Track(size=3, name="header"),
            Track(name="content"),
            Track(size=2, name="footer"),
        ],
    )

    areas = {
        "sidebar": "start-sidebar end-sidebar start-content end-content",
        "footer": "start-footer end-footer 1 1",
    }

    sidebar = "start-sidebar end-sidebar start-content end-content"

    from rich.console import Console

    console = Console()
    print(console.options)

    grid.reflow(console, console.width, console.height)
