from __future__ import annotations

from rich.console import Console, ConsoleOptions, RenderableType, RenderResult
from rich.segment import Segment
from rich.style import StyleType

from textual.reactive import Reactive
from textual.renderables._tab_headers import TabHeadersRenderable, Tab
from textual.renderables.underline_bar import UnderlineBar
from textual.widget import Widget


class TabsRenderable:
    def __init__(
        self,
        tabs: list[Tab],
        active_tab_name: str,
        active_bar_style: StyleType,
        inactive_bar_style: StyleType,
        inactive_text_opacity: float,
        tab_padding: int | None,
        bar_offset: float,
    ):
        self.tabs = tabs
        self.active_tab_name = active_tab_name
        self.active_bar_style = active_bar_style
        self.inactive_bar_style = inactive_bar_style
        self.inactive_text_opacity = inactive_text_opacity
        self.tab_padding = tab_padding
        self.bar_offset = bar_offset

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        headers = TabHeadersRenderable(
            self.tabs,
            active_tab_name=self.active_tab_name,
            tab_padding=self.tab_padding,
            inactive_tab_opacity=self.inactive_text_opacity,
        )
        yield from console.render(headers)
        yield Segment.line()

        ranges = headers.get_ranges()
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


class Tabs(Widget):
    """Horizontal tabs"""

    active_tab_name: Reactive[str] = Reactive("")
    bar_offset: Reactive[float] = Reactive(0.0)

    def __init__(
        self,
        tabs: list[Tab],
        active_tab: str | None = None,
        active_bar_style: StyleType = "#1BB152",
        inactive_bar_style: StyleType = "#455058",
        tab_padding: int | None = None,
        inactive_text_opacity: float = 0.5,
    ) -> None:
        super().__init__()
        self.tabs = tabs

        # TODO: Handle empty tabs
        self.active_tab_name = active_tab or tabs[0]
        self.active_bar_style = active_bar_style
        self.inactive_bar_style = inactive_bar_style
        self.bar_offset = float(self.get_tab_index(active_tab) or 0)
        self.inactive_text_opacity = inactive_text_opacity

        self._used = False
        self.tab_padding = tab_padding

    def action_activate_tab(self, target_tab_name: str) -> None:
        self.active_tab_name = target_tab_name

    def watch_active_tab_name(self, tab_name: str) -> None:
        target_tab_index = self.get_tab_index(tab_name)
        self.animate(
            "bar_offset", float(target_tab_index), easing="out_cubic", duration=0.3
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
            active_bar_style=self.active_bar_style,
            inactive_bar_style=self.inactive_bar_style,
            bar_offset=self.bar_offset,
            inactive_text_opacity=self.inactive_text_opacity,
        )
