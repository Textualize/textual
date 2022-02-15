from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from rich.cells import cell_len
from rich.console import Console, ConsoleOptions, RenderResult
from rich.style import Style
from rich.text import Text

from textual import log
from textual._loop import loop_first


@dataclass
class Tab:
    label: str
    name: str | None = None

    def __post_init__(self):
        if self.name is None:
            self.name = self.label

    def __str__(self):
        return self.label


class TabHeadersRenderable:
    def __init__(
        self,
        tabs: Iterable[Tab],
        *,
        active_tab_name: str | None = None,
        width: int | None = None,
        tab_padding: int = 1,
    ):
        self.tabs = {tab.name: tab for tab in tabs}
        self.active_tab_name = active_tab_name or next(iter(self.tabs))
        self.width = width
        self.tab_padding = tab_padding

        self._range_cache: dict[str, tuple[int, int]] = {}

    def get_active_range(self) -> tuple[int, int]:
        return self._range_cache[self.active_tab_name]

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        width = self.width or options.max_width
        tabs = self.tabs
        tab_values = self.tabs.values()

        # There's padding at each side of a label
        padding_len = 2 * self.tab_padding * len(tabs)

        # The total length of the labels, including their padding
        total_len = sum(cell_len(header.label) for header in tab_values) + padding_len

        # The amount of space left to distribute around tabs
        free_space = width - total_len

        # The gap between each tab (not including padding)
        space_per_gap = free_space // (len(tabs) + 1)

        gap = Text(" " * space_per_gap, end="")
        lpad = rpad = Text(" " * self.tab_padding, end="")

        char_index = space_per_gap + self.tab_padding
        for tab_index, (is_first, tab) in enumerate(loop_first(tab_values)):
            if is_first:
                yield gap
            yield lpad

            tab_content = Text(
                tab.label,
                end="",
                style=Style(
                    color="#f0f0f0", bgcolor="#021720", meta={"@click": "highlight"}
                ),
            )

            # Cache and move to next label
            len_label = len(tab.label)
            self._range_cache[tab.name] = (char_index, char_index + len_label)
            char_index += len_label + space_per_gap + self.tab_padding * 2

            if tab.name == self.active_tab_name:
                yield tab_content
            else:
                dimmed_tab_content = tab_content
                segments = list(console.render(dimmed_tab_content))
                log(segments)
                yield from segments

            yield rpad
            yield gap


if __name__ == "__main__":
    console = Console()

    h = TabHeadersRenderable(
        [
            Tab("One"),
            Tab("Two"),
            Tab("Three"),
        ]
    )

    console.print(h)
