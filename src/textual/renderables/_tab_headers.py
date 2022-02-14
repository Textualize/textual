from __future__ import annotations

from dataclasses import dataclass

from rich.cells import cell_len
from rich.console import Console, ConsoleOptions, RenderResult
from rich.style import Style
from rich.text import Text

from textual import log
from textual._loop import loop_first
from textual.renderables.opacity import Opacity


@dataclass
class Tab:
    title: str
    active: bool = False
    key: str | None = None

    def __post_init__(self):
        if self.key is None:
            self.key = self.title

    def __str__(self):
        return self.title


class TabHeadersRenderable:
    def __init__(
        self,
        tabs: list[Tab],
        *,
        width: int | None = None,
        tab_padding: int = 1,
    ):
        self.tabs = tabs
        self.width = width
        self.tab_padding = tab_padding

    def action_highlight(self):
        log("highlighted!")

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        width = self.width or options.max_width
        tabs = self.tabs

        padding_len = self.tab_padding * len(tabs)
        total_len = sum(cell_len(header.title) for header in tabs) + padding_len

        free_space = width - total_len
        space_per_gap = free_space // (len(tabs) + 1)

        gap = Text(" " * space_per_gap, end="")
        lpad = rpad = Text(" " * self.tab_padding, end="")

        for is_first, tab in loop_first(tabs):
            if is_first:
                yield gap
            yield lpad
            tab_content = Text(
                tab.title, end="", style=Style(meta={"@click": "highlight"})
            )
            yield tab_content
            # if tab.active:
            #     yield tab_content
            # else:
            #     dimmed_tab_content = Opacity(tab_content, opacity=.2)
            #     yield from console.render(dimmed_tab_content)
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
