from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from rich.cells import cell_len
from rich.console import Console, ConsoleOptions, RenderResult
from rich.style import Style, StyleType
from rich.text import Text

from textual.renderables.opacity import Opacity
from textual.renderables.underline_bar import UnderlineBar


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
        active_tab_name: str,
        active_bar_style: StyleType,
        inactive_bar_style: StyleType,
        inactive_text_opacity: float,
        tab_padding: int | None,
        bar_offset: float,
        width: int | None = None,
    ):
        self.tabs = {tab.name: tab for tab in tabs}
        self.active_tab_name = active_tab_name or next(iter(self.tabs))
        self.active_bar_style = active_bar_style
        self.inactive_bar_style = inactive_bar_style
        self.bar_offset = bar_offset
        self.width = width
        self.tab_padding = tab_padding
        self.inactive_text_opacity = inactive_text_opacity

        self._range_cache: dict[str, tuple[int, int]] = {}

    def get_active_range(self) -> tuple[int, int]:
        return self._range_cache[self.active_tab_name]

    def get_ranges(self):
        return self._range_cache

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        width = self.width or options.max_width
        tabs = self.tabs
        tab_values = self.tabs.values()

        if self.tab_padding is None:
            total_len = sum(cell_len(header.label) for header in tab_values)
            free_space = width - total_len
            label_pad = (free_space // len(tabs) + 1) // 2
        else:
            label_pad = self.tab_padding

        pad = Text(" " * label_pad, end="")

        char_index = label_pad
        for tab_index, tab in enumerate(tab_values):
            yield pad
            tab_content = Text(
                tab.label,
                end="",
                style=Style(
                    color="#f0f0f0",
                    bgcolor="#262626",
                    meta={"@click": f"activate_tab('{tab.name}')"},
                ),
            )

            # Cache and move to next label
            len_label = cell_len(tab.label)
            self._range_cache[tab.name] = (char_index, char_index + len_label)
            char_index += len_label + label_pad * 2

            if tab.name == self.active_tab_name:
                yield tab_content
            else:
                dimmed_tab_content = Opacity(
                    tab_content, opacity=self.inactive_text_opacity
                )
                segments = list(console.render(dimmed_tab_content))
                yield from segments

            yield pad

        ranges = self.get_ranges()
        tab_index = int(self.bar_offset)
        next_tab_index = (tab_index + 1) % len(ranges)

        range_values = list(ranges.values())

        tab1_start, tab1_end = range_values[tab_index]
        tab2_start, tab2_end = range_values[next_tab_index]

        bar_start = tab1_start + (tab2_start - tab1_start) * (
            self.bar_offset - tab_index
        )
        bar_end = tab1_end + (tab2_end - tab1_end) * (self.bar_offset - tab_index)

        underline = UnderlineBar(
            highlight_range=(bar_start, bar_end),
            highlight_style=self.active_bar_style,
            background_style=self.inactive_bar_style,
        )
        yield from console.render(underline)
