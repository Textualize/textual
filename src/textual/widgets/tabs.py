from __future__ import annotations

from rich.console import Console, ConsoleOptions, RenderableType, RenderResult
from rich.segment import Segment

from textual import log
from textual.renderables._tab_headers import TabHeadersRenderable, Tab
from textual.renderables.underline_bar import UnderlineBar
from textual.widget import Widget


class TabsRenderable:
    def __init__(self, headers: list[Tab]):
        self.headers = headers

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        headers = TabHeadersRenderable(tabs=self.headers)
        underline = UnderlineBar(highlight_range=(19, 26), highlight_style="#95d52a")
        yield from console.render(headers)
        yield Segment.line()
        yield from console.render(underline)


class Tabs(Widget):
    def __init__(self, headers: list[Tab]):
        self.headers = headers
        super().__init__()

    def action_highlight(self, header: str):
        log(f"action_header_clicked {header}")

    def render(self) -> RenderableType:
        return TabsRenderable(self.headers)
