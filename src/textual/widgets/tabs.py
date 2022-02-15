from __future__ import annotations

from rich.console import Console, ConsoleOptions, RenderableType, RenderResult
from rich.segment import Segment

from textual import log, events
from textual.reactive import Reactive
from textual.renderables._tab_headers import TabHeadersRenderable, Tab
from textual.renderables.underline_bar import UnderlineBar
from textual.widget import Widget


class TabsRenderable:
    def __init__(self, tabs: list[Tab], active_tab_name: str):
        self.tabs = tabs
        self.active_tab_name = active_tab_name

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        headers = TabHeadersRenderable(self.tabs, active_tab_name=self.active_tab_name)
        yield from console.render(headers)
        yield Segment.line()
        # TODO: How do we choose highlight_style?
        highlight_range = headers.get_active_range()
        underline = UnderlineBar(
            highlight_range=highlight_range, highlight_style="#95d52a"
        )
        yield from console.render(underline)


class Tabs(Widget):
    def __init__(self, tabs: list[Tab]):
        self.tabs = tabs
        super().__init__()

    active_tab_name = Reactive("")

    def render(self) -> RenderableType:
        return TabsRenderable(self.tabs, active_tab_name=self.active_tab_name)
