from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Iterable

from importlib_metadata import version
from rich.align import Align
from rich.console import Console, ConsoleOptions, RenderResult
from rich.markup import escape
from rich.rule import Rule
from rich.segment import Segment, Segments
from rich.style import Style
from rich.styled import Styled
from rich.table import Table
from rich.text import Text
from typing_extensions import Literal

from textual._log import LogGroup

DevConsoleMessageLevel = Literal["info", "warning", "error"]


class DevConsoleHeader:
    def __init__(self, verbose: bool = False) -> None:
        self.verbose = verbose

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        preamble = Text.from_markup(
            f"[bold]Textual Development Console [magenta]v{version('textual')}\n"
            "[magenta]Run a Textual app with [reverse]textual run --dev my_app.py[/] to connect.\n"
            "[magenta]Press [reverse]Ctrl+C[/] to quit."
        )
        if self.verbose:
            preamble.append(Text.from_markup("\n[cyan]Verbose logs enabled"))
        render_options = options.update(width=options.max_width - 4)
        lines = console.render_lines(preamble, render_options)

        new_line = Segment.line()
        padding = Segment("▌", Style.parse("bright_magenta"))

        for line in lines:
            yield padding
            yield from line
            yield new_line


class DevConsoleLog:
    """Renderable representing a single log message

    Args:
        segments: The segments to display
        path: The path of the file on the client that the log call was made from
        line_number: The line number of the file on the client the log call was made from
        unix_timestamp: Seconds since January 1st 1970
    """

    def __init__(
        self,
        segments: Iterable[Segment],
        path: str,
        line_number: int,
        unix_timestamp: int,
        group: int,
        verbosity: int,
        severity: int,
    ) -> None:
        self.segments = segments
        self.path = path
        self.line_number = line_number
        self.unix_timestamp = unix_timestamp
        self.group = group
        self.verbosity = verbosity
        self.severity = severity

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        local_time = datetime.fromtimestamp(self.unix_timestamp)
        table = Table.grid(expand=True)

        file_link = escape(f"file://{Path(self.path).absolute()}")
        file_and_line = escape(f"{Path(self.path).name}:{self.line_number}")
        group = LogGroup(self.group).name
        time = local_time.time()

        group_text = Text(group)
        if group == "WARNING":
            group_text.stylize("bold yellow reverse")
        elif group == "ERROR":
            group_text.stylize("bold red reverse")
        else:
            group_text.stylize("dim")

        log_message = Text.assemble((f"[{time}]", "dim"), " ", group_text)

        table.add_row(
            log_message,
            Align.right(
                Text(f"{file_and_line}", style=Style(dim=True, link=file_link))
            ),
        )
        yield table

        if group == "PRINT":
            yield Styled(Segments(self.segments), "bold")
        else:
            yield from self.segments


class DevConsoleNotice:
    """Renderable for messages written by the devtools console itself

    Args:
        message: The message to display
        level: The message level ("info", "warning", or "error").
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
