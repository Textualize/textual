from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from importlib_metadata import version
from rich.containers import Renderables
from rich.style import Style
from rich.text import Text

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal

from rich.console import Console
from rich.align import Align
from rich.console import ConsoleOptions, RenderResult
from rich.markup import escape
from rich.rule import Rule
from rich.segment import Segment, Segments
from rich.table import Table

DevConsoleMessageLevel = Literal["info", "warning", "error"]


class DevConsoleHeader:
    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        lines = Renderables(
            [
                f"[bold]Textual Development Console [magenta]v{version('textual')}",
                "[magenta]Run a Textual app with the environment variable [b]TEXTUAL=devtools[/] to connect.",
                "[magenta]Press [b]Ctrl+C[/] to quit.",
            ]
        )
        render_options = options.update(width=options.max_width - 4)
        lines = console.render_lines(lines, render_options)
        new_line = Segment("\n")
        padding = Segment("▌", Style.parse("bright_magenta"))
        for line in lines:
            yield padding
            yield from line
            yield new_line


class DevConsoleLog:
    """Renderable representing a single log message

    Args:
        segments (Iterable[Segment]): The segments to display
        path (str): The path of the file on the client that the log call was made from
        line_number (int): The line number of the file on the client the log call was made from
        unix_timestamp (int): Seconds since January 1st 1970
    """

    def __init__(
        self,
        segments: Iterable[Segment],
        path: str,
        line_number: int,
        unix_timestamp: int,
    ) -> None:
        self.segments = segments
        self.path = path
        self.line_number = line_number
        self.unix_timestamp = unix_timestamp

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        local_time = (
            datetime.fromtimestamp(self.unix_timestamp)
            .replace(tzinfo=timezone.utc)
            .astimezone(tz=datetime.now().astimezone().tzinfo)
        )
        timezone_name = local_time.tzname()
        table = Table.grid(expand=True)
        table.add_column()
        table.add_column()
        file_link = escape(f"file://{Path(self.path).absolute()}")
        file_and_line = escape(f"{Path(self.path).name}:{self.line_number}")
        table.add_row(
            f"[dim]{local_time.time()} {timezone_name}",
            Align.right(
                Text(f"{file_and_line}", style=Style(dim=True, link=file_link))
            ),
        )
        yield table
        yield Segments(self.segments)


class DevConsoleNotice:
    """Renderable for messages written by the devtools console itself

    Args:
        message (str): The message to display
        level (DevtoolsMessageLevel): The message level ("info", "warning", or "error").
            Determines colors used to render the message and the perceived importance.
    """

    def __init__(self, message: str, *, level: DevConsoleMessageLevel = "info") -> None:
        self.message = message
        self.level = level

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        level_to_style = {
            "info": "dim",
            "warning": "yellow",
            "error": "red",
        }
        yield Rule(self.message, style=level_to_style.get(self.level, "dim"))
