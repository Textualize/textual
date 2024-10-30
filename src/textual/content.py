"""
Content is Textual's equivalent to Rich's Text object, with support for transparency.

The interface is (will be) similar, with the major difference that is *immutable*.
This will make some operations slower, but dramatically improve cache-ability.

TBD: Is this a public facing API or an internal one?

"""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from itertools import zip_longest
from marshal import loads
from operator import itemgetter
from typing import Any, Iterable, NamedTuple, Sequence, cast

import rich.repr
from rich._wrap import divide_line
from rich.cells import set_cell_size
from rich.console import JustifyMethod, OverflowMethod
from rich.segment import Segment, Segments
from rich.style import Style as RichStyle

from textual._cells import cell_len
from textual._loop import loop_last
from textual.color import Color

_re_whitespace = re.compile(r"\s+$")


def _justify_lines(
    lines: list[Content],
    width: int,
    justify: "JustifyMethod" = "left",
    overflow: "OverflowMethod" = "fold",
) -> list[Content]:
    """Justify and overflow text to a given width.

    Args:
        console (Console): Console instance.
        width (int): Number of cells available per line.
        justify (str, optional): Default justify method for text: "left", "center", "full" or "right". Defaults to "left".
        overflow (str, optional): Default overflow for text: "crop", "fold", or "ellipsis". Defaults to "fold".

    """

    for line in lines:
        assert isinstance(line._spans, list)

    if justify == "left":
        lines = [line.truncate(width, overflow=overflow, pad=True) for line in lines]

    elif justify == "center":
        lines = [
            line.rstrip()
            .truncate(width, overflow=overflow)
            .pad_left((width - cell_len(line.plain)) // 2)
            .pad_right(width - cell_len(line.plain))
            for line in lines
        ]
    elif justify == "right":
        lines = [
            line.rstrip()
            .truncate(width, overflow=overflow)
            .pad_left(width - cell_len(line.plain))
            for line in lines
        ]

    elif justify == "full":
        new_lines = lines.copy()
        for line_index, line in enumerate(new_lines):
            words = line.split(" ")
            words_size = sum(cell_len(word.plain) for word in words)
            num_spaces = len(words) - 1
            spaces = [1 for _ in range(num_spaces)]
            index = 0
            if spaces:
                while words_size + num_spaces < width:
                    spaces[len(spaces) - index - 1] += 1
                    num_spaces += 1
                    index = (index + 1) % len(spaces)
            tokens: list[Content] = []
            for index, (word, next_word) in enumerate(zip_longest(words, words[1:])):
                tokens.append(word)
                if index < len(spaces):
                    end_style = next_word.get_style_at_offset(-1)
                    tokens.append(
                        Content(" " * spaces[index], [Span(0, index, end_style)])
                    )

            new_lines[line_index] = Content("").join(tokens)
        return new_lines
    return lines


@rich.repr.auto
@dataclass(frozen=True)
class Style:
    """Represent a content style (color and other attributes)."""

    background: Color = Color(0, 0, 0, ansi=-1)
    foreground: Color = Color(255, 255, 255, ansi=-1)
    bold: bool | None = None
    dim: bool | None = None
    italic: bool | None = None
    underline: bool | None = None
    strike: bool | None = None
    link: str | None = None
    _meta: bytes | None = None

    def __rich_repr__(self) -> rich.repr.Result:
        yield self.background
        yield self.foreground
        yield "bold", self.bold, None
        yield "dim", self.dim, None
        yield "italic", self.italic, None
        yield "underline", self.underline, None
        yield "strike", self.strike, None

    @lru_cache(maxsize=1024)
    def __add__(self, other: object) -> Style:
        if not isinstance(other, Style):
            return NotImplemented
        new_style = Style(
            self.background + other.background,
            self.foreground + other.foreground,
            self.bold if other.bold is None else other.bold,
            self.dim if other.dim is None else other.dim,
            self.italic if other.italic is None else other.italic,
            self.underline if other.underline is None else other.underline,
            self.strike if other.strike is None else other.strike,
            self.link if other.link is None else other.link,
            self._meta if other._meta is None else other._meta,
        )
        return new_style

    @property
    def rich_style(self) -> RichStyle:
        return RichStyle(
            color=self.foreground.rich_color,
            bgcolor=self.background.rich_color,
            bold=self.bold,
            dim=self.dim,
            italic=self.italic,
            underline=self.underline,
            strike=self.strike,
            link=self.link,
            meta=self.meta,
        )

    @classmethod
    def combine(cls, styles: Iterable[Style]) -> Style:
        """Add a number of styles and get the result."""
        iter_styles = iter(styles)
        return sum(iter_styles, next(iter_styles))

    @property
    def meta(self) -> dict[str, Any]:
        """Get meta information (can not be changed after construction)."""
        return {} if self._meta is None else cast(dict[str, Any], loads(self._meta))


class Span(NamedTuple):
    """A style applied to a range of character offsets."""

    start: int
    end: int
    style: Style


@rich.repr.auto
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
        assert isinstance(self._spans, list)
        assert all(isinstance(span, Span) for span in self._spans)
        self._cell_length = cell_length

    def __len__(self) -> int:
        return len(self.plain)

    def __bool__(self) -> bool:
        return self._text == []

    def __hash__(self) -> int:
        return hash(self._text)

    def __rich_repr__(self) -> rich.repr.Result:
        yield self._text
        yield "spans", self._spans, []

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

    def __getitem__(self, slice: int | slice) -> Content:
        def get_text_at(offset: int) -> "Content":
            _Span = Span
            content = Content(
                self.plain[offset],
                spans=[
                    _Span(0, 1, style)
                    for start, end, style in self._spans
                    if end > offset >= start
                ],
            )
            return content

        if isinstance(slice, int):
            return get_text_at(slice)
        else:
            start, stop, step = slice.indices(len(self.plain))
            if step == 1:
                lines = self.divide([start, stop])
                return lines[1]
            else:
                # This would be a bit of work to implement efficiently
                # For now, its not required
                raise TypeError("slices with step!=1 are not supported")

    def __add__(self, other: object) -> Content:
        if isinstance(other, str):
            return Content(self._text + other, self._spans.copy())
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
                (
                    self.cell_length + other._cell_length
                    if other._cell_length is not None
                    else None
                ),
            )
            return content
        return NotImplemented

    @classmethod
    def _trim_spans(cls, text: str, spans: list[Span]) -> list[Span]:
        """Remove or modify any spans that are over the end of the text."""
        max_offset = len(text)
        _Span = Span
        spans = [
            (
                span
                if span.end < max_offset
                else _Span(span.start, min(max_offset, span.end), span.style)
            )
            for span in spans
            if span.start < max_offset
        ]
        return spans

    def join(self, lines: Iterable[Content]) -> Content:
        text: list[str] = []
        spans: list[Span] = []

        def iter_content() -> Iterable[Content]:
            if self.plain:
                for last, line in loop_last(lines):
                    yield line
                    if not last:
                        yield self
            else:
                yield from lines

        extend_text = text.extend
        extend_spans = spans.extend
        offset = 0
        _Span = Span

        for content in iter_content():
            extend_text(content._text)
            extend_spans(
                _Span(offset + start, offset + end, style)
                for start, end, style in content._spans
            )
            offset += len(text)
        return Content("".join(text), spans, offset)

    def get_style_at_offset(self, offset: int) -> Style:
        """Get the style of a character at give offset.

        Args:
            offset (int): Offset in to text (negative indexing supported)

        Returns:
            Style: A Style instance.
        """
        # TODO: This is a little inefficient, it is only used by full justify
        if offset < 0:
            offset = len(self) + offset

        style = Style()
        for start, end, span_style in self._spans:
            if end > offset >= start:
                style += span_style
        return style

    def truncate(
        self,
        max_width: int,
        *,
        overflow: OverflowMethod = "fold",
        pad: bool = False,
    ) -> Content:
        if overflow == "ignore":
            return self

        length = cell_len(self.plain)
        text = self.plain
        if length > max_width:
            if overflow == "ellipsis":
                text = set_cell_size(self.plain, max_width - 1) + "…"
            else:
                text = set_cell_size(self.plain, max_width)
        if pad and length < max_width:
            spaces = max_width - length
            text = f"{self.plain}{' ' * spaces}"
            length = len(self.plain)
        spans = self._trim_spans(text, self._spans)
        return Content(text, spans)

    def pad_left(self, count: int, character: str = " ") -> Content:
        """Pad the left with a given character.

        Args:
            count (int): Number of characters to pad.
            character (str, optional): Character to pad with. Defaults to " ".
        """
        assert len(character) == 1, "Character must be a string of length 1"
        if count:
            text = f"{character * count}{self.plain}"
            _Span = Span
            spans = [
                _Span(start + count, end + count, style)
                for start, end, style in self._spans
            ]
            return Content(text, spans)
        return self

    def pad_right(self, count: int, character: str = " ") -> Content:
        """Pad the right with a given character.

        Args:
            count (int): Number of characters to pad.
            character (str, optional): Character to pad with. Defaults to " ".
        """
        assert len(character) == 1, "Character must be a string of length 1"
        if count:
            return Content(f"{self.plain}{character * count}", self._spans)
        return self

    def right_crop(self, amount: int = 1) -> Content:
        """Remove a number of characters from the end of the text."""
        max_offset = len(self.plain) - amount
        _Span = Span
        spans = [
            (
                span
                if span.end < max_offset
                else _Span(span.start, min(max_offset, span.end), span.style)
            )
            for span in self._spans
            if span.start < max_offset
        ]
        text = self.plain[:-amount]
        length = None if self._cell_length is None else self._cell_length - amount
        return Content(text, spans, length)

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

    def render(self, base_style: Style, end: str = "\n") -> Iterable[tuple[str, Style]]:
        if not self._spans:
            yield self._text, base_style
            if end:
                yield end, base_style
            return

        enumerated_spans = list(enumerate(self._spans, 1))
        style_map = {index: span.style for index, span in enumerated_spans}
        style_map[0] = base_style
        text = self.plain

        spans = [
            (0, False, 0),
            *((span.start, False, index) for index, span in enumerated_spans),
            *((span.end, True, index) for index, span in enumerated_spans),
            (len(text), True, 0),
        ]
        spans.sort(key=itemgetter(0, 1))

        stack: list[int] = [0]
        stack_append = stack.append
        stack_pop = stack.remove

        style_cache: dict[tuple[Style, ...], Style] = {}
        style_cache_get = style_cache.get
        combine = Style.combine

        def get_current_style() -> Style:
            """Construct current style from stack."""
            styles = tuple(style_map[_style_id] for _style_id in sorted(stack))
            cached_style = style_cache_get(styles)
            if cached_style is not None:
                return cached_style
            current_style = combine(styles)
            style_cache[styles] = current_style
            return current_style

        for (offset, leaving, style_id), (next_offset, _, _) in zip(spans, spans[1:]):
            if leaving:
                stack_pop(style_id)
            else:
                stack_append(style_id)
            if next_offset > offset:
                yield text[offset:next_offset], get_current_style()
        if end:
            yield end, base_style

    def render_segments(self, base_style: Style, end: str = "\n") -> list[Segment]:
        _Segment = Segment
        segments = [
            _Segment(text, style.rich_style)
            for text, style in self.render(base_style, end)
        ]
        return segments

    def divide(self, offsets: Sequence[int]) -> list[Content]:
        if not offsets:
            return [self]

        text = self.plain
        text_length = len(text)
        divide_offsets = [0, *offsets, text_length]
        line_ranges = list(zip(divide_offsets, divide_offsets[1:]))

        new_lines = [Content(text[start:end]) for start, end in line_ranges]
        if not self._spans:
            return new_lines

        _line_appends = [line._spans.append for line in new_lines]
        line_count = len(line_ranges)
        _Span = Span

        for span_start, span_end, style in self._spans:
            lower_bound = 0
            upper_bound = line_count
            start_line_no = (lower_bound + upper_bound) // 2

            while True:
                line_start, line_end = line_ranges[start_line_no]
                if span_start < line_start:
                    upper_bound = start_line_no - 1
                elif span_start > line_end:
                    lower_bound = start_line_no + 1
                else:
                    break
                start_line_no = (lower_bound + upper_bound) // 2

            if span_end < line_end:
                end_line_no = start_line_no
            else:
                end_line_no = lower_bound = start_line_no
                upper_bound = line_count

                while True:
                    line_start, line_end = line_ranges[end_line_no]
                    if span_end < line_start:
                        upper_bound = end_line_no - 1
                    elif span_end > line_end:
                        lower_bound = end_line_no + 1
                    else:
                        break
                    end_line_no = (lower_bound + upper_bound) // 2

            for line_no in range(start_line_no, end_line_no + 1):
                line_start, line_end = line_ranges[line_no]
                new_start = max(0, span_start - line_start)
                new_end = min(span_end - line_start, line_end - line_start)
                if new_end > new_start:
                    _line_appends[line_no](_Span(new_start, new_end, style))

        return new_lines

    def split(
        self,
        separator: str = "\n",
        *,
        include_separator: bool = False,
        allow_blank: bool = False,
    ) -> list[Content]:
        """Split rich text in to lines, preserving styles.

        Args:
            separator (str, optional): String to split on. Defaults to "\\\\n".
            include_separator (bool, optional): Include the separator in the lines. Defaults to False.
            allow_blank (bool, optional): Return a blank line if the text ends with a separator. Defaults to False.

        Returns:
            List[RichText]: A list of rich text, one per line of the original.
        """
        assert separator, "separator must not be empty"

        text = self.plain
        if separator not in text:
            return [self]

        if include_separator:
            lines = self.divide(
                [match.end() for match in re.finditer(re.escape(separator), text)]
            )
        else:

            def flatten_spans() -> Iterable[int]:
                for match in re.finditer(re.escape(separator), text):
                    start, end = match.span()
                    yield start
                    yield end

            lines = [
                line
                for line in self.divide(list(flatten_spans()))
                if line.plain != separator
            ]

        if not allow_blank and text.endswith(separator):
            lines.pop()

        return lines

    def rstrip(self) -> Content:
        """Strip whitespace from end of text."""
        text = self.plain.rstrip()
        return Content(text, self._trim_spans(text, self._spans))

    def rstrip_end(self, size: int) -> Content:
        """Remove whitespace beyond a certain width at the end of the text.

        Args:
            size (int): The desired size of the text.
        """
        text_length = len(self)
        if text_length > size:
            excess = text_length - size
            whitespace_match = _re_whitespace.search(self.plain)
            if whitespace_match is not None:
                whitespace_count = len(whitespace_match.group(0))
                return self.right_crop(min(whitespace_count, excess))
        return self

    def wrap(
        self,
        width: int,
        justify: JustifyMethod = "left",
        overflow: OverflowMethod = "fold",
        no_wrap: bool = False,
    ) -> list[Content]:
        lines: list[Content] = []
        for line in self.split(allow_blank=True):
            # if "\t" in line:
            #     line.expand_tabs(tab_size)
            if no_wrap:
                new_lines = [line]
            else:
                offsets = divide_line(line._text, width, fold=overflow == "fold")
                new_lines = line.divide(offsets)
            new_lines = [line.rstrip_end(width) for line in new_lines]
            new_lines = _justify_lines(
                new_lines, width, justify=justify, overflow=overflow
            )
            new_lines = [line.truncate(width, overflow=overflow) for line in new_lines]
            lines.extend(new_lines)
        return lines

    def highlight_regex(
        self,
        re_highlight: re.Pattern[str] | str,
        style: Style,
    ) -> Content:
        spans: list[Span] = self._spans.copy()
        append_span = spans.append
        _Span = Span
        plain = self.plain
        if isinstance(re_highlight, str):
            re_highlight = re.compile(re_highlight)
        for match in re_highlight.finditer(plain):
            start, end = match.span()

            if end > start:
                append_span(_Span(start, end, style))
        return Content(self._text, spans)


if __name__ == "__main__":
    from rich import print

    TEXT = """I must not fear.
Fear is the mind-killer.
Fear is the little-death that brings total obliteration.
I will face my fear.
I will permit it to pass over me and through me.
And when it has gone past, I will turn the inner eye to see its path.
Where the fear has gone there will be nothing. Only I will remain."""

    content = Content(TEXT)
    content = content.highlight_regex("F..r", Style(bold=True))

    lines = content.wrap(30, justify="left")
    for line in lines:
        segments = Segments(line.render_segments(Style()))
        print(segments)
