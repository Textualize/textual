from __future__ import annotations

from typing import Iterable

import rich.repr
from rich.console import Console, ConsoleOptions, RenderResult
from rich.highlighter import ReprHighlighter
from rich.markup import render
from rich.text import Text
from rich.tree import Tree

_highlighter = ReprHighlighter()


def _markup_and_highlight(text: str) -> Text:
    """Highlight and render markup in a string of text, returning
    a styled Text object.

    Args:
        text: The text to highlight and markup.

    Returns:
        The Text, with highlighting and markup applied.
    """
    return _highlighter(render(text))


class Example:
    """Renderable for an example, which can appear below bullet points in
    the help text.

    Attributes:
        markup: The markup to display for this example
    """

    def __init__(self, markup: str) -> None:
        self.markup: str = markup

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        yield _markup_and_highlight(f"  [dim]e.g. [/][i]{self.markup}[/]")


@rich.repr.auto
class Bullet:
    """Renderable for a single 'bullet point' containing information and optionally some examples
        pertaining to that information.

    Attributes:
        markup: The markup to display
        examples: An optional list of examples
            to display below this bullet.
    """

    def __init__(self, markup: str, examples: Iterable[Example] | None = None) -> None:
        self.markup: str = markup
        self.examples: Iterable[Example] | None = [] if examples is None else examples

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        yield _markup_and_highlight(self.markup)
        if self.examples is not None:
            yield from self.examples


@rich.repr.auto
class HelpText:
    """Renderable for help text - the user is shown this when they
    encounter a style-related error (e.g. setting a style property to an invalid
    value).

    Attributes:
        summary: A succinct summary of the issue.
        bullets: Bullet points which provide additional
            context around the issue. These are rendered below the summary. Defaults to None.
    """

    def __init__(
        self, summary: str, *, bullets: Iterable[Bullet] | None = None
    ) -> None:
        self.summary: str = summary
        self.bullets: Iterable[Bullet] | None = bullets or []

    def __str__(self) -> str:
        return self.summary

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        tree = Tree(_markup_and_highlight(f"[b blue]{self.summary}"), guide_style="dim")
        if self.bullets is not None:
            for bullet in self.bullets:
                tree.add(bullet)
        yield tree
