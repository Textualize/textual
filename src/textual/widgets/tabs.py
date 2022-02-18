from __future__ import annotations

import string
from dataclasses import dataclass
from types import SimpleNamespace
from typing import Iterable, cast

from rich.cells import cell_len
from rich.console import Console, ConsoleOptions, RenderableType, RenderResult
from rich.segment import Segment
from rich.style import StyleType, Style
from rich.text import Text

from textual import events
from textual._layout_resolve import layout_resolve, Edge
from textual.keys import Keys
from textual.reactive import Reactive
from textual.renderables.opacity import Opacity
from textual.renderables.underline_bar import UnderlineBar
from textual.widget import Widget


__all__ = ["Tab", "Tabs"]


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

    def get_underline_bar(self, console):
        if self.tabs:
            ranges = self._label_range_cache
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
        tab_values = self.tabs.values()

        space = cast(
            Edge, SimpleNamespace(min_size=1, size=self.tab_padding or None, fraction=1)
        )
        edges = []
        for tab in tab_values:
            tab = cast(
                Edge,
                SimpleNamespace(size=cell_len(tab.label), min_size=1, fraction=None),
            )
            edges.extend([space, tab, space])

        spacing = layout_resolve(width, edges=edges)

        active_tab_style = console.get_style(self.active_tab_style)
        inactive_tab_style = console.get_style(self.inactive_tab_style)

        label_cell_cursor = 0
        for tab_index, tab in enumerate(tab_values):
            tab_edge_index = tab_index * 3 + 1

            len_label_text = spacing[tab_edge_index]
            lpad = spacing[tab_edge_index - 1]
            rpad = spacing[tab_edge_index + 1]

            label_left_padding = Text(" " * lpad, end="")
            label_right_padding = Text(" " * rpad, end="")

            padded_label = f"{label_left_padding}{tab.label}{label_right_padding}"
            if tab.name == self.active_tab_name:
                yield Text(padded_label, end="", style=active_tab_style)
            else:
                tab_content = Text(
                    padded_label,
                    end="",
                    style=inactive_tab_style
                    + Style.from_meta({"@click": f"range_clicked('{tab.name}')"}),
                )
                dimmed_tab_content = Opacity(
                    tab_content, opacity=self.inactive_text_opacity
                )
                segments = console.render(dimmed_tab_content)
                yield from segments

            # Cache the position of the label text within this tab
            label_cell_cursor += lpad
            self._label_range_cache[tab.name] = (
                label_cell_cursor,
                label_cell_cursor + len_label_text,
            )
            label_cell_cursor += len_label_text + rpad

            # Cache the position of the whole tab, i.e. the range that can be clicked
            self._selection_range_cache[tab.name] = (
                label_cell_cursor - lpad,
                label_cell_cursor + len_label_text + rpad,
            )


class Tabs(Widget):
    """Widget which displays a set of horizontal tabs.

    Args:
        tabs (list[Tab]): A list of Tab objects defining the tabs which should be rendered.
        active_tab (str | None): The name of the tab that should be active on first render.
        active_tab_style (StyleType): Style to apply to the label of the active tab.
        active_bar_style (StyleType): Style to apply to the underline of the active tab.
        inactive_tab_style (StyleType): Style to apply to the label of inactive tabs.
        inactive_bar_style (StyleType): Style to apply to the underline of inactive tabs.
        inactive_text_opacity (float): Opacity of the labels of inactive tabs.
        animation_duration (float): The duration of the tab change animation, in seconds.
        animation_function (str): The easing function to use for the tab change animation.
        tab_padding (int | None): The horizontal padding at the side of each tab. If None,
            tabs will automatically receive padding such that they fit available space.
        search_by_first_character (bool): If True, entering a character on your keyboard
            will activate the next tab (in left-to-right order) with a label starting with
            that character.
    """

    DEFAULT_STYLES = "height: 2;"

    _active_tab_name: Reactive[str | None] = Reactive("")
    _bar_offset: Reactive[float] = Reactive(0.0)

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
        search_by_first_character: bool = True,
    ) -> None:
        super().__init__()
        self.tabs = tabs

        self._bar_offset = float(self.get_tab_index(active_tab) or 0)
        self._active_tab_name = active_tab or next(iter(self.tabs), None)

        self.active_tab_style = active_tab_style
        self.active_bar_style = active_bar_style

        self.inactive_bar_style = inactive_bar_style
        self.inactive_tab_style = inactive_tab_style
        self.inactive_text_opacity = inactive_text_opacity

        self.animation_function = animation_function
        self.animation_duration = animation_duration

        self.tab_padding = tab_padding

        self.search_by_first_character = search_by_first_character

    def on_key(self, event: events.Key) -> None:
        if not self.tabs:
            event.prevent_default()
            return

        if event.key == Keys.Right:
            self.activate_next_tab()
        elif event.key == Keys.Left:
            self.activate_previous_tab()
        elif event.key in string.digits:
            self.activate_tab_by_number(int(event.key))
        elif self.search_by_first_character:
            self.activate_tab_by_first_char(event.key)

        event.prevent_default()

    def activate_next_tab(self) -> None:
        current_tab_index = self.get_tab_index(self._active_tab_name)
        next_tab_index = (current_tab_index + 1) % len(self.tabs)
        next_tab_name = self.tabs[next_tab_index].name
        self._active_tab_name = next_tab_name

    def activate_previous_tab(self) -> None:
        current_tab_index = self.get_tab_index(self._active_tab_name)
        previous_tab_index = current_tab_index - 1
        previous_tab_name = self.tabs[previous_tab_index].name
        self._active_tab_name = previous_tab_name

    def activate_tab_by_first_char(self, char: str) -> None:
        def find_next_matching_tab(
            char: str, start: int | None, end: int | None
        ) -> Tab | None:
            for tab in self.tabs[start:end]:
                if tab.label.lower().startswith(char.lower()):
                    return tab

        current_tab_index = self.get_tab_index(self._active_tab_name)
        next_tab_index = (current_tab_index + 1) % len(self.tabs)

        next_matching_tab = find_next_matching_tab(char, next_tab_index, None)
        if not next_matching_tab:
            next_matching_tab = find_next_matching_tab(char, None, current_tab_index)

        if next_matching_tab:
            self._active_tab_name = next_matching_tab.name

    def activate_tab_by_number(self, tab_number: int) -> None:
        if tab_number > len(self.tabs):
            return
        if tab_number == 0 and len(self.tabs) >= 10:
            tab_number = 10
        self._active_tab_name = self.tabs[tab_number - 1].name

    def action_range_clicked(self, target_tab_name: str) -> None:
        self._active_tab_name = target_tab_name

    def watch__active_tab_name(self, tab_name: str) -> None:
        target_tab_index = self.get_tab_index(tab_name)
        self.animate(
            "_bar_offset",
            float(target_tab_index),
            easing=self.animation_function,
            duration=self.animation_duration,
        )

    def get_tab_index(self, tab_name: str) -> int:
        return next((i for i, tab in enumerate(self.tabs) if tab.name == tab_name), 0)

    def render(self) -> RenderableType:
        return TabsRenderable(
            self.tabs,
            tab_padding=self.tab_padding,
            active_tab_name=self._active_tab_name,
            active_tab_style=self.active_tab_style,
            active_bar_style=self.active_bar_style,
            inactive_tab_style=self.inactive_tab_style,
            inactive_bar_style=self.inactive_bar_style,
            bar_offset=self._bar_offset,
            inactive_text_opacity=self.inactive_text_opacity,
        )
