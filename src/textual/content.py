"""
Content is Textual's equivalent to Rich's Text object, with support for transparency.

The interface is (will be) similar, with the major difference that is *immutable*.
This will make some operations slower, but dramatically improve cache-ability.

TBD: Is this a public facing API or an internal one?

"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import NamedTuple

from textual._cells import cell_len
from textual.color import TRANSPARENT, Color


@dataclass(frozen=True)
class Style:
    """Represent a content style (color and other attributes)."""

    background: Color = TRANSPARENT
    foreground: Color = TRANSPARENT
    bold: bool | None = None
    italic: bool | None = None
    underline: bool | None = None
    strike: bool | None = None
    link: str | None = None
    meta: bytes | None = None

    @lru_cache(maxsize=1024)
    def __add__(self, other: object) -> Style:
        if not isinstance(other, Style):
            return NotImplemented
        new_style = Style(
            self.background + other.background,
            self.foreground + other.foreground,
            self.bold if other.bold is None else other.bold,
            self.italic if other.italic is None else other.italic,
            self.underline if other.underline is None else other.underline,
            self.strike if other.strike is None else other.strike,
            self.link if other.link is None else other.link,
            self.meta if other.meta is None else other.meta,
        )
        return new_style


class Span(NamedTuple):
    """A style applied to a range of character offsets."""

    start: int
    end: int
    style: Style


class Content:
    """Text content with marked up spans.

    This object can be considered immutable, although it might update its internal state
    in a way that is consistent with immutability.

    """

    def __init__(
        self, text: str, spans: list[Span] | None = None, cell_length: int | None = None
    ) -> None:
        self._text: str = text
        self._spans: list[Span] = [] if spans is None else spans
        self._cell_length = cell_length

    def __len__(self) -> int:
        return len(self.plain)

    def __bool__(self) -> bool:
        return self._text == []

    def __hash__(self) -> int:
        return hash(self._text)

    @property
    def cell_length(self) -> int:
        """The cell length of the content."""
        if self._cell_length is None:
            self._cell_length = cell_len(self.plain)
        return self._cell_length

    @property
    def plain(self) -> str:
        """Get the text as a single string."""
        return self._text

    def stylize(self, style: Style, start: int = 0, end: int | None = None) -> Content:
        """Apply a style to the text, or a portion of the text.

        Args:
            style (Union[str, Style]): Style instance or style definition to apply.
            start (int): Start offset (negative indexing is supported). Defaults to 0.
            end (Optional[int], optional): End offset (negative indexing is supported), or None for end of text. Defaults to None.
        """
        length = len(self)
        if start < 0:
            start = length + start
        if end is None:
            end = length
        if end < 0:
            end = length + end
        if start >= length or end <= start:
            # Span not in text or not valid
            return self
        return Content(
            self.plain,
            [*self._spans, Span(start, length if length < end else end, style)],
        )

    def __add__(self, other: object) -> Content:
        if isinstance(other, str):
            return Content(self._text + other, self._spans)
        if isinstance(other, Content):
            offset = len(self.plain)
            content = Content(
                self.plain + other.plain,
                [
                    *self._spans,
                    *[
                        Span(start + offset, end + offset, style)
                        for start, end, style in other._spans
                    ],
                ],
            )
            return content
        return NotImplemented
