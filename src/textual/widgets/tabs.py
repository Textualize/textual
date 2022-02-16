from __future__ import annotations

from rich.console import Console, ConsoleOptions, RenderableType, RenderResult
from rich.segment import Segment

from textual import log
from textual.reactive import Reactive
from textual.renderables._tab_headers import TabHeadersRenderable, Tab
from textual.renderables.underline_bar import UnderlineBar
from textual.widget import Widget


class TabsRenderable:
    def __init__(
        self,
        tabs: list[Tab],
        active_tab_name: str,
        tab_padding: int | None = None,
        bar_offset: float = 0.0,
    ):
        self.tabs = tabs
        self.active_tab_name = active_tab_name
        self.tab_padding = tab_padding
        self.bar_offset = bar_offset

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        headers = TabHeadersRenderable(
            self.tabs,
            active_tab_name=self.active_tab_name,
            tab_padding=self.tab_padding,
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
            highlight_style="#95d52a",
        )
        yield from console.render(underline)


class Tabs(Widget):
    """Widget for displaying tab headers"""

    active_tab_name: Reactive[str] = Reactive("")
    bar_offset: Reactive[float] = Reactive(0.0)

    def __init__(
        self,
        tabs: list[Tab],
        active_tab: str | None = None,
        tab_padding: int | None = None,
    ) -> None:
        super().__init__()
        self.tabs = tabs

        self.active_tab_name = active_tab or tabs[0].name
        self.bar_offset = float(self.get_tab_index(active_tab) or 0)

        self._used = False
        self.tab_padding = tab_padding

    def action_activate_tab(self, target_tab_name: str) -> None:
        self.active_tab_name = target_tab_name

    def watch_active_tab_name(self, tab_name: str) -> None:
        target_tab_index = self.get_tab_index(tab_name)
        log("bar_offset", self.bar_offset)
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
            bar_offset=self.bar_offset,
        )
