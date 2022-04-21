from __future__ import annotations

from typing import Iterable

from rich.console import Console, ConsoleOptions, RenderResult

from rich.highlighter import ReprHighlighter
from rich.markup import render
from rich.text import Text

_highlighter = ReprHighlighter()


def _markup_and_highlight(text: str) -> Text:
    return _highlighter(render(text))


class Example:
    def __init__(self, markup: str) -> None:
        self.markup = markup

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        yield _markup_and_highlight(f"    [dim]e.g. [/][i]{self.markup}[/]")


class Bullet:
    def __init__(self, markup: str, examples: Iterable[Example] | None = None) -> None:
        self.markup = markup
        self.examples = [] if examples is None else examples

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        yield _markup_and_highlight(f"• {self.markup}")
        yield from self.examples


class HelpText:
    def __init__(self, *bullet_points: Bullet) -> None:
        self.bullet_points = bullet_points

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        yield from self.bullet_points
