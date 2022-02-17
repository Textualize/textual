from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from rich.cells import cell_len
from rich.console import Console, ConsoleOptions, RenderableType, RenderResult
from rich.segment import Segment
from rich.style import StyleType, Style
from rich.text import Text

from textual.reactive import Reactive
from textual.renderables._tab_headers import Tab
from textual.renderables.opacity import Opacity
from textual.renderables.underline_bar import UnderlineBar
from textual.widget import Widget


@dataclass
class Tab:
    label: str
    name: str | None = None

    def __post_init__(self):
        if self.name is None:
            self.name = self.label

    def __str__(self):
        return self.label


class TabsRenderable:
    def __init__(
        self,
        tabs: Iterable[Tab],
        *,
        active_tab_name: str,
        active_tab_style: StyleType,
        active_bar_style: StyleType,
        inactive_tab_style: StyleType,
        inactive_bar_style: StyleType,
        inactive_text_opacity: float,
        tab_padding: int | None,
        bar_offset: float,
        width: int | None = None,
    ):
        self.tabs = {tab.name: tab for tab in tabs}

        try:
            self.active_tab_name = active_tab_name or next(iter(self.tabs))
        except StopIteration:
            self.active_tab_name = None

        self.active_tab_style = active_tab_style
        self.active_bar_style = active_bar_style

        self.inactive_tab_style = inactive_tab_style
        self.inactive_bar_style = inactive_bar_style

        self.bar_offset = bar_offset
        self.width = width
        self.tab_padding = tab_padding
        self.inactive_text_opacity = inactive_text_opacity

        self._label_range_cache: dict[str, tuple[int, int]] = {}
        self._selection_range_cache: dict[str, tuple[int, int]] = {}

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        if self.tabs:
            yield from self.get_tab_headers(console, options)
        yield Segment.line()
        yield from self.get_underline_bar(console)

    def get_active_range(self) -> tuple[int, int]:
        return self._label_range_cache[self.active_tab_name]

    def get_ranges(self):
        return self._label_range_cache

    def get_underline_bar(self, console):
        if self.tabs:
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
        else:
            bar_start = 0
            bar_end = 0
        underline = UnderlineBar(
            highlight_range=(bar_start, bar_end),
            highlight_style=self.active_bar_style,
            background_style=self.inactive_bar_style,
            clickable_ranges=self._selection_range_cache,
        )
        yield from console.render(underline)

    def get_tab_headers(self, console, options):
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
        active_tab_style = console.get_style(self.active_tab_style)
        inactive_tab_style = console.get_style(self.inactive_tab_style)
        for tab_index, tab in enumerate(tab_values):
            # Cache and move to next label
            len_label = cell_len(tab.label)
            self._label_range_cache[tab.name] = (char_index, char_index + len_label)
            self._selection_range_cache[tab.name] = (
                char_index - label_pad,
                char_index + len_label + label_pad,
            )

            char_index += len_label + label_pad * 2

            if tab.name == self.active_tab_name:
                tab_content = Text(
                    f"{pad}{tab.label}{pad}",
                    end="",
                    style=active_tab_style,
                )
                yield tab_content
            else:
                tab_content = Text(
                    f"{pad}{tab.label}{pad}",
                    end="",
                    style=inactive_tab_style
                    + Style.from_meta({"@click": f"activate_tab('{tab.name}')"}),
                )
                dimmed_tab_content = Opacity(
                    tab_content, opacity=self.inactive_text_opacity
                )
                segments = list(console.render(dimmed_tab_content))
                yield from segments


class Tabs(Widget):
    """Horizontal tabs"""

    DEFAULT_STYLES = "height: 2;"

    active_tab_name: Reactive[str | None] = Reactive("")
    bar_offset: Reactive[float] = Reactive(0.0)

    def __init__(
        self,
        tabs: list[Tab],
        active_tab: str | None = None,
        active_tab_style: StyleType = "#f0f0f0 on #021720",
        active_bar_style: StyleType = "#1BB152",
        inactive_tab_style: StyleType = "#f0f0f0 on #021720",
        inactive_bar_style: StyleType = "#455058",
        inactive_text_opacity: float = 0.5,
        animation_duration: float = 0.3,
        animation_function: str = "out_cubic",
        tab_padding: int | None = None,
    ) -> None:
        super().__init__()
        self.tabs = tabs

        self.active_tab_name = active_tab or next(iter(self.tabs), None)
        self.active_tab_style = active_tab_style
        self.active_bar_style = active_bar_style

        self.inactive_bar_style = inactive_bar_style
        self.inactive_tab_style = inactive_tab_style
        self.inactive_text_opacity = inactive_text_opacity

        self.bar_offset = float(self.get_tab_index(active_tab) or 0)

        self.animation_function = animation_function
        self.animation_duration = animation_duration

        self._used = False
        self.tab_padding = tab_padding

    def action_activate_tab(self, target_tab_name: str) -> None:
        self.active_tab_name = target_tab_name

    def watch_active_tab_name(self, tab_name: str) -> None:
        target_tab_index = self.get_tab_index(tab_name)
        self.animate(
            "bar_offset",
            float(target_tab_index),
            easing=self.animation_function,
            duration=self.animation_duration,
        )
        self._used = True

    def get_tab_index(self, tab_name: str) -> int:
        target_tab_index = next(
            (i for i, tab in enumerate(self.tabs) if tab.name == tab_name), 0
        )
        return target_tab_index

    def render(self) -> RenderableType:
        return TabsRenderable(
            self.tabs,
            tab_padding=self.tab_padding,
            active_tab_name=self.active_tab_name,
            active_tab_style=self.active_tab_style,
            active_bar_style=self.active_bar_style,
            inactive_tab_style=self.inactive_tab_style,
            inactive_bar_style=self.inactive_bar_style,
            bar_offset=self.bar_offset,
            inactive_text_opacity=self.inactive_text_opacity,
        )
