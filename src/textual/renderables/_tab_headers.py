from __future__ import annotations

from rich.cells import cell_len
from rich.console import Console, ConsoleOptions, RenderResult
from rich.padding import Padding
from rich.text import Text

from textual._loop import loop_first


class TabHeader:
    def __init__(self, headers: list[str], *, width: int | None = None):
        self.headers = headers
        self.width = width

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        width = self.width or options.max_width
        headers = self.headers
        free_space = width - sum(cell_len(header) for header in headers)
        space_per_gap = free_space // (len(headers) + 1)
        gap = Text(" " * space_per_gap, end="")
        pad = Text(" ", end="")
        for is_first, header in loop_first(headers):
            if is_first:
                yield gap
            yield pad
            yield Text(header, end="")
            yield pad
            yield gap


if __name__ == "__main__":
    console = Console()

    header = TabHeader(
        headers=[
            "One",
            "Two",
            "Three",
        ]
    )

    console.print(header)
