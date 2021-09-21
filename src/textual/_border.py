from __future__ import annotations

from rich.console import Console, ConsoleOptions, RenderResult

from .draw import DrawStyle


class Border:
    def __init__(self, sides: tuple[bool, bool, bool, bool], draw: DrawStyle):
        pass

    def __rich_console__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> "RenderResult":
        pass
