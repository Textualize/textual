"""
Content is Textual's equivalent to Rich's Text object, with support for transparency.

The interface is (will be) similar, with the major difference that is *immutable*.
This will make some operations slower, but dramatically improve cache-ability.

TBD: Is this a public facing API or an internal one?

"""

from __future__ import annotations

import re
from functools import lru_cache
from operator import itemgetter
from typing import TYPE_CHECKING, Callable, Iterable, NamedTuple, Sequence, Union

import rich.repr
from rich._wrap import divide_line
from rich.cells import set_cell_size
from rich.console import OverflowMethod
from rich.segment import Segment, Segments
from rich.terminal_theme import TerminalTheme
from rich.text import Text
from typing_extensions import Final, TypeAlias

from textual._cells import cell_len
from textual._context import active_app
from textual._loop import loop_last
from textual.color import Color
from textual.css.types import TextAlign
from textual.selection import Selection
from textual.strip import Strip
from textual.style import Style
from textual.visual import Visual

if TYPE_CHECKING:
    from textual.widget import Widget

_re_whitespace = re.compile(r"\s+$")

ContentType: TypeAlias = Union["Content", str]

ANSI_DEFAULT = Style(
    background=Color(0, 0, 0, 0, ansi=-1), foreground=Color(0, 0, 0, 0, ansi=-1)
)

TRANSPARENT_STYLE = Style()

_STRIP_CONTROL_CODES: Final = [
    7,  # Bell
    8,  # Backspace
    11,  # Vertical tab
    12,  # Form feed
    13,  # Carriage return
]
_CONTROL_STRIP_TRANSLATE: Final = {
    _codepoint: None for _codepoint in _STRIP_CONTROL_CODES
}


def strip_control_codes(
    text: str, _translate_table: dict[int, None] = _CONTROL_STRIP_TRANSLATE
) -> str:
    """Remove control codes from text.

    Args:
        text (str): A string possibly contain control codes.

    Returns:
        str: String with control codes removed.
    """
    return text.translate(_translate_table)


@rich.repr.auto
class Span(NamedTuple):
    """A style applied to a range of character offsets."""

    start: int
    end: int
    style: Style | str

    def __rich_repr__(self) -> rich.repr.Result:
        yield self.start
        yield self.end
        yield "style", self.style

    def extend(self, cells: int) -> "Span":
        """Extend the span by the given number of cells.

        Args:
            cells (int): Additional space to add to end of span.

        Returns:
            Span: A span.
        """
        if cells:
            start, end, style = self
            return Span(start, end + cells, style)
        return self


@rich.repr.auto
class Content(Visual):
    """Text content with marked up spans.

    This object can be considered immutable, although it might update its internal state
    in a way that is consistent with immutability.

    """

    __slots__ = ["_text", "_spans", "_cell_length", "_align", "_no_wrap", "_ellipsis"]

    _NORMALIZE_TEXT_ALIGN = {"start": "left", "end": "right", "justify": "full"}

    def __init__(
        self,
        text: str,
        spans: list[Span] | None = None,
        cell_length: int | None = None,
        align: TextAlign = "left",
        no_wrap: bool = False,
        ellipsis: bool = False,
    ) -> None:
        """

        Args:
            text: text content.
            spans: Optional list of spans.
            cell_length: Cell length of text if known, otherwise `None`.
            align: Align method.
            no_wrap: Disable wrapping.
            ellipsis: Add ellipsis when wrapping is disabled and text is cropped.
        """
        self._text: str = strip_control_codes(text)
        self._spans: list[Span] = [] if spans is None else spans
        self._cell_length = cell_length
        self._align = align
        self._no_wrap = no_wrap
        self._ellipsis = ellipsis

    def __str__(self) -> str:
        return self._text

    @property
    def markup(self) -> str:
        """Get Content markup to render this Text.

        Returns:
            str: A string potentially creating markup tags.
        """
        from textual.markup import escape

        output: list[str] = []

        plain = self.plain
        markup_spans = [
            (0, False, None),
            *((span.start, False, span.style) for span in self._spans),
            *((span.end, True, span.style) for span in self._spans),
            (len(plain), True, None),
        ]
        markup_spans.sort(key=itemgetter(0, 1))
        position = 0
        append = output.append
        for offset, closing, style in markup_spans:
            if offset > position:
                append(escape(plain[position:offset]))
                position = offset
            if style:
                append(f"[/{style}]" if closing else f"[{style}]")
        markup = "".join(output)
        return markup

    @classmethod
    def from_markup(
        cls,
        markup: str,
        align: TextAlign = "left",
        no_wrap: bool = False,
        ellipsis: bool = False,
    ) -> Content:
        """Create content from Textual markup.

        !!! note
            Textual markup is not the same as Rich markup. Use [Text.parse] to parse Rich Console markup.


        Args:
            markup: Textual Markup
            align: Align method.
            no_wrap: Disable wrapping.
            ellipsis: Add ellipsis when wrapping is disabled and text is cropped.

        Returns:
            New Content instance.
        """
        from textual.markup import to_content

        content = to_content(markup, align=align, no_wrap=no_wrap, ellipsis=ellipsis)
        return content

    @classmethod
    def from_rich_text(
        cls,
        text: str | Text,
        align: TextAlign = "left",
        no_wrap: bool = False,
        ellipsis: bool = False,
    ) -> Content:
        """Create equivalent Visual Content for str or Text.

        Args:
            text: String or Rich Text.
            align: Align method.
            no_wrap: Disable wrapping.
            ellipsis: Add ellipsis when wrapping is disabled and text is cropped.

        Returns:
            New Content.
        """
        if isinstance(text, str):
            text = Text.from_markup(text)

        ansi_theme: TerminalTheme | None = None

        if text._spans:
            try:
                ansi_theme = active_app.get().ansi_theme
            except LookupError:
                ansi_theme = None
            spans = [
                Span(
                    start,
                    end,
                    (
                        style
                        if isinstance(style, str)
                        else Style.from_rich_style(style, ansi_theme)
                    ),
                )
                for start, end, style in text._spans
            ]
        else:
            spans = []

        content = cls(
            text.plain,
            spans,
            align=align,
            no_wrap=no_wrap,
            ellipsis=ellipsis,
        )
        if text.style:
            try:
                ansi_theme = active_app.get().ansi_theme
            except LookupError:
                ansi_theme = None
            content = content.stylize_before(
                text.style
                if isinstance(text.style, str)
                else Style.from_rich_style(text.style, ansi_theme)
            )
        return content

    @classmethod
    def styled(
        cls,
        text: str,
        style: Style | str = "",
        cell_length: int | None = None,
        align: TextAlign = "left",
        no_wrap: bool = False,
        ellipsis: bool = False,
    ) -> Content:
        """Create a Content instance from a single styled piece of text.

        Args:
            text: String content.
            style: Desired style.
            cell_length: Cell length of text if known, otherwise `None`.
            align: Text alignment.
            no_wrap: Disable wrapping.
            ellipsis: Add ellipsis when wrapping is disabled and text is cropped.

        Returns:
            New Content instance.
        """
        if not text:
            return Content("", align=align, no_wrap=no_wrap, ellipsis=ellipsis)
        span_length = cell_len(text) if cell_length is None else cell_length
        new_content = cls(
            text,
            [Span(0, span_length, style)],
            span_length,
            align=align,
            no_wrap=no_wrap,
            ellipsis=ellipsis,
        )
        return new_content

    def __eq__(self, other: object) -> bool:
        if isinstance(other, str):
            return self.plain == other
        elif isinstance(other, Content):
            return self.plain == other.plain
        return str(self) == str(other)

    def get_optimal_width(self, widget: Widget, container_width: int) -> int:
        """Get optimal width of the visual to display its content. Part of the Textual Visual protocol.

        Args:
            widget: Parent widget.
            container_size: The size of the container.

        Returns:
            A width in cells.

        """
        lines = self.without_spans.split("\n")
        return max(line.cell_length for line in lines)

    def get_height(self, widget: Widget, width: int) -> int:
        """Get the height of the visual if rendered with the given width. Part of the Textual Visual protocol.

        Args:
            widget: Parent widget.
            width: Width of visual.

        Returns:
            A height in lines.
        """
        lines = self._wrap_and_format(width)
        return len(lines)

    def _wrap_and_format(
        self,
        width: int,
        align: TextAlign = "left",
        overflow: OverflowMethod = "fold",
        no_wrap: bool = False,
        tab_size: int = 8,
        selection: Selection | None = None,
        selection_style: Style | None = None,
    ) -> list[FormattedLine]:
        """Wraps the text and applies formatting.

        Args:
            width: Desired width.
            align: Text alignment.
            overflow: Overflow method.
            no_wrap: Disabled wrapping.
            tab_size: Cell with of tabs.
            selection: Selection information or `None` if no selection.
            selection_style: Selection style, or `None` if no selection.

        Returns:
            List of formatted lines.
        """
        output_lines: list[FormattedLine] = []

        if selection is not None:
            get_span = selection.get_span
        else:

            def get_span(y: int) -> tuple[int, int] | None:
                return None

        for y, line in enumerate(self.split(allow_blank=True)):
            if selection_style is not None and (span := get_span(y)) is not None:
                start, end = span
                if end == -1:
                    end = len(line.plain)
                line = line.stylize(selection_style, start, end)

            content_line = FormattedLine(
                line.expand_tabs(tab_size), width, y=y, align=align
            )

            if no_wrap:
                new_lines = [content_line]
            else:
                offsets = divide_line(line.plain, width, fold=overflow == "fold")
                divided_lines = content_line.content.divide(offsets)
                new_lines = [
                    FormattedLine(
                        content.rstrip_end(width), width, offset, y, align=align
                    )
                    for content, offset in zip(divided_lines, [0, *offsets])
                ]
                new_lines[-1].line_end = True

            output_lines.extend(new_lines)

        return output_lines

    def render_strips(
        self,
        widget: Widget,
        width: int,
        height: int | None,
        style: Style,
    ) -> list[Strip]:
        if not width:
            return []

        selection = widget.selection
        if selection is not None:
            selection_style = Style.from_rich_style(
                widget.screen.get_component_rich_style("screen--selection")
            )

        else:
            selection_style = None

        styles = widget.styles
        align = (
            widget.styles.text_align if styles.has_rule("text_align") else self._align
        )
        lines = self._wrap_and_format(
            width,
            align=align,
            overflow=(
                ("ellipsis" if self._ellipsis else "crop") if self._no_wrap else "fold"
            ),
            no_wrap=False,
            tab_size=8,
            selection=widget.selection,
            selection_style=selection_style,
        )

        if height is not None:
            lines = lines[:height]

        strip_lines = [line.to_strip(widget, style) for line in lines]
        return strip_lines

    def __len__(self) -> int:
        return len(self.plain)

    def __bool__(self) -> bool:
        return self._text != ""

    def __hash__(self) -> int:
        return hash(self._text)

    def __rich_repr__(self) -> rich.repr.Result:
        yield self._text
        yield "spans", self._spans, []

    @property
    def spans(self) -> Sequence[Span]:
        """A sequence of spans used to markup regions of the content."""
        return self._spans

    @property
    def cell_length(self) -> int:
        """The cell length of the content."""
        if self._cell_length is None:
            self._cell_length = cell_len(self.plain)
        return self._cell_length

    @property
    def align(self) -> TextAlign:
        """Text alignment."""
        return self._align

    @property
    def no_wrap(self) -> bool:
        """Disable text wrapping?"""
        return self._no_wrap

    @property
    def ellipsis(self) -> bool:
        """Crop text with ellipsis?"""
        return self._ellipsis

    @property
    def plain(self) -> str:
        """Get the text as a single string."""
        return self._text

    @property
    def without_spans(self) -> Content:
        """The content with no spans"""
        return Content(
            self.plain,
            [],
            self._cell_length,
            align=self._align,
            no_wrap=self._no_wrap,
            ellipsis=self._ellipsis,
        )

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

    def append(self, content: Content | str) -> Content:
        """Append text or content to this content.

        Note this is a little inefficient, if you have many strings to append, consider [`join`][textual.content.Content.join].

        Args:
            content: A content instance, or a string.

        Returns:
            New content.
        """
        if isinstance(content, str):
            return Content(
                f"{self.plain}{content}",
                self._spans,
                (
                    None
                    if self._cell_length is None
                    else self._cell_length + cell_len(content)
                ),
                align=self.align,
                no_wrap=self.no_wrap,
                ellipsis=self.ellipsis,
            )
        return Content("").join([self, content])

    def append_text(self, text: str, style: Style | str = "") -> Content:
        return self.append(Content.styled(text, style))

    def join(self, lines: Iterable[Content]) -> Content:
        """Join an iterable of content.

        Args:
            lines (_type_): An iterable of content instances.

        Returns:
            A single Content instance, containing all of the lines.

        """
        text: list[str] = []
        spans: list[Span] = []

        def iter_content() -> Iterable[Content]:
            """Iterate the lines, optionally inserting the separator."""
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

        total_cell_length: int | None = self._cell_length

        for content in iter_content():
            extend_text(content._text)
            extend_spans(
                _Span(offset + start, offset + end, style)
                for start, end, style in content._spans
            )
            offset += len(content._text)
            if total_cell_length is not None:
                total_cell_length = (
                    None
                    if content._cell_length is None
                    else total_cell_length + content._cell_length
                )

        return Content("".join(text), spans, total_cell_length)

    def get_style_at_offset(self, offset: int) -> Style:
        """Get the style of a character at give offset.

        Args:
            offset (int): Offset into text (negative indexing supported)

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
            content = Content(
                text,
                spans,
                None if self._cell_length is None else self._cell_length + count,
            )
            return content

        return self

    def extend_right(self, count: int, character: str = " ") -> Content:
        """Add repeating characters (typically spaces) to the content with the style(s) of the last character.

        Args:
            count: Number of spaces.
            character: Character to add with.

        Returns:
            A Content instance.
        """
        if count:
            plain = self.plain
            plain_len = len(plain)
            return Content(
                f"{plain}{character * count}",
                [
                    (span.extend(count) if span.end == plain_len else span)
                    for span in self._spans
                ],
                None if self._cell_length is None else self._cell_length + count,
            )
        return self

    def pad_right(self, count: int, character: str = " ") -> Content:
        """Pad the right with a given character.

        Args:
            count (int): Number of characters to pad.
            character (str, optional): Character to pad with. Defaults to " ".
        """
        assert len(character) == 1, "Character must be a string of length 1"
        if count:
            return Content(
                f"{self.plain}{character * count}",
                self._spans,
                None if self._cell_length is None else self._cell_length + count,
            )
        return self

    def center(self, width: int, ellipsis: bool = False) -> Content:
        """Align a line to the center.

        Args:
            width: Desired width of output.
            ellipsis: Insert ellipsis if content is truncated.

        Returns:
            New line Content.
        """
        content = self.rstrip().truncate(
            width, overflow="ellipsis" if ellipsis else "fold"
        )
        left = (width - content.cell_length) // 2
        right = width - left
        content = content.pad_left(left).pad_right(right)
        return content

    def right(self, width: int, ellipsis: bool = False) -> Content:
        """Align a line to the right.

        Args:
            width: Desired width of output.
            ellipsis: Insert ellipsis if content is truncated.

        Returns:
            New line Content.
        """
        content = self.rstrip().truncate(
            width, overflow="ellipsis" if ellipsis else "fold"
        )
        content = content.pad_left(width - content.cell_length)
        return content

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

    def stylize(
        self, style: Style | str, start: int = 0, end: int | None = None
    ) -> Content:
        """Apply a style to the text, or a portion of the text.

        Args:
            style (Union[str, Style]): Style instance or style definition to apply.
            start (int): Start offset (negative indexing is supported). Defaults to 0.
            end (Optional[int], optional): End offset (negative indexing is supported), or None for end of text. Defaults to None.
        """
        if not style:
            return self
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

    def stylize_before(
        self,
        style: Style | str,
        start: int = 0,
        end: int | None = None,
    ) -> Content:
        """Apply a style to the text, or a portion of the text. Styles will be applied before other styles already present.

        Args:
            style (Union[str, Style]): Style instance or style definition to apply.
            start (int): Start offset (negative indexing is supported). Defaults to 0.
            end (Optional[int], optional): End offset (negative indexing is supported), or None for end of text. Defaults to None.
        """
        if not style:
            return self
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
            [Span(start, length if length < end else end, style), *self._spans],
        )

    def render(
        self,
        base_style: Style,
        end: str = "\n",
        parse_style: Callable[[str], Style] | None = None,
    ) -> Iterable[tuple[str, Style]]:
        if not self._spans:
            yield (self._text, base_style)
            if end:
                yield end, base_style
            return

        if parse_style is None:
            try:
                app = active_app.get()
            except LookupError:
                css_variables = {}
            else:
                css_variables = app.get_css_variables()
            # TODO: Update when we add Content.from_markup

            @lru_cache(maxsize=1024)
            def get_style(style: str, /) -> Style:
                try:
                    visual_style = Style.parse(style, css_variables)
                except Exception:
                    visual_style = Style.null()
                return visual_style

        else:
            get_style = parse_style

        enumerated_spans = list(enumerate(self._spans, 1))
        style_map = {
            index: (
                get_style(span.style) if isinstance(span.style, str) else span.style
            )
            for index, span in enumerated_spans
        }
        style_map[0] = base_style
        text = self.plain

        spans = [
            (0, False, 0),
            *((span.start, False, index) for index, span in enumerated_spans),
            *((span.end, True, index) for index, span in enumerated_spans),
            (len(text), True, 0),
        ]
        spans.sort(key=itemgetter(0, 1))

        stack: list[int] = []
        stack_append = stack.append
        stack_pop = stack.remove

        style_cache: dict[tuple[int, ...], Style] = {}
        style_cache_get = style_cache.get
        combine = Style.combine

        def get_current_style() -> Style:
            """Construct current style from stack."""
            cache_key = tuple(stack)
            cached_style = style_cache_get(cache_key)
            if cached_style is not None:
                return cached_style
            styles = [style_map[_style_id] for _style_id in cache_key]
            current_style = combine(styles)
            style_cache[cache_key] = current_style
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

    def render_segments(self, base_style: Style, end: str = "") -> list[Segment]:
        _Segment = Segment
        segments = [
            _Segment(text, (style.rich_style if style else None))
            for text, style in self.render(base_style, end)
        ]
        return segments

    def divide(
        self,
        offsets: Sequence[int],
    ) -> list[Content]:
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
        """Split rich text into lines, preserving styles.

        Args:
            separator (str, optional): String to split on. Defaults to "\\\\n".
            include_separator (bool, optional): Include the separator in the lines. Defaults to False.
            allow_blank (bool, optional): Return a blank line if the text ends with a separator. Defaults to False.

        Returns:
            List[Content]: A list of Content, one per line of the original.
        """
        assert separator, "separator must not be empty"

        text = self.plain
        if separator not in text:
            return [self]

        if include_separator:
            lines = self.divide(
                [match.end() for match in re.finditer(re.escape(separator), text)],
            )
        else:

            def flatten_spans() -> Iterable[int]:
                for match in re.finditer(re.escape(separator), text):
                    yield from match.span()

            lines = [
                line
                for line in self.divide(list(flatten_spans()))
                if line.plain != separator
            ]

        if not allow_blank and text.endswith(separator):
            lines.pop()

        return lines

    def rstrip(self, chars: str | None = None) -> Content:
        """Strip characters from end of text."""
        text = self.plain.rstrip(chars)
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

    def extend_style(self, spaces: int) -> Content:
        """Extend the Text given number of spaces where the spaces have the same style as the last character.

        Args:
            spaces (int): Number of spaces to add to the Text.
        """
        if spaces <= 0:
            return self
        spans = self._spans
        new_spaces = " " * spaces
        if spans:
            end_offset = len(self)
            spans = [
                span.extend(spaces) if span.end >= end_offset else span
                for span in spans
            ]
            return Content(self._text + new_spaces, spans, self.cell_length + spaces)
        return Content(self._text + new_spaces, self._spans, self._cell_length)

    def expand_tabs(self, tab_size: int = 8) -> Content:
        """Converts tabs to spaces.

        Args:
            tab_size (int, optional): Size of tabs. Defaults to 8.

        """
        if "\t" not in self.plain:
            return self

        new_text: list[Content] = []
        append = new_text.append

        for line in self.split("\n", include_separator=True):
            if "\t" not in line.plain:
                append(line)
            else:
                cell_position = 0
                parts = line.split("\t", include_separator=True)
                for part in parts:
                    if part.plain.endswith("\t"):
                        part = Content(
                            part._text[-1][:-1] + " ", part._spans, part._cell_length
                        )
                        cell_position += part.cell_length
                        tab_remainder = cell_position % tab_size
                        if tab_remainder:
                            spaces = tab_size - tab_remainder
                            part = part.extend_style(spaces)
                            cell_position += spaces
                    else:
                        cell_position += part.cell_length
                    append(part)

        content = Content("").join(new_text)
        return content

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


class FormattedLine:
    """A line of content with additional formatting information."""

    def __init__(
        self,
        content: Content,
        width: int,
        x: int = 0,
        y: int = 0,
        align: TextAlign = "left",
        line_end: bool = False,
        link_style: Style | None = None,
    ) -> None:
        self.content = content
        self.width = width
        self.x = x
        self.y = y
        self.align = align
        self.line_end = line_end
        self.link_style = link_style

    @property
    def plain(self) -> str:
        return self.content.plain

    def to_strip(self, widget: Widget, style: Style) -> Strip:
        _Segment = Segment
        align = self.align
        width = self.width
        pad_left = pad_right = 0
        content = self.content
        x = self.x
        y = self.y

        if align in ("start", "left") or (align == "justify" and self.line_end):
            pass

        elif align == "center":
            excess_space = width - self.content.cell_length
            pad_left = excess_space // 2
            pad_right = excess_space - pad_left

        elif align in ("end", "right"):
            pad_left = width - self.content.cell_length

        elif align == "justify":
            words = content.split(" ", include_separator=False)
            words_size = sum(cell_len(word.plain.rstrip(" ")) for word in words)
            num_spaces = len(words) - 1
            spaces = [1] * num_spaces
            index = 0
            if spaces:
                while words_size + num_spaces < width:
                    spaces[len(spaces) - index - 1] += 1
                    num_spaces += 1
                    index = (index + 1) % len(spaces)

            segments: list[Segment] = []
            add_segment = segments.append
            x = self.x
            for index, word in enumerate(words):
                for text, text_style in word.render(style, end=""):
                    add_segment(
                        _Segment(
                            text, (style + text_style).rich_style_with_offset(x, y)
                        )
                    )
                    x += len(text) + 1
                if index < len(spaces) and (pad := spaces[index]):
                    add_segment(_Segment(" " * pad, (style + text_style).rich_style))

            strip = Strip(self._apply_link_style(widget, segments), width)
            return strip

        segments = (
            [Segment(" " * pad_left, style.background_style.rich_style)]
            if pad_left
            else []
        )
        add_segment = segments.append
        for text, text_style in content.render(style, end=""):
            add_segment(
                _Segment(text, (style + text_style).rich_style_with_offset(x, y))
            )
            x += len(text)

        if pad_right:
            segments.append(
                _Segment(" " * pad_right, style.background_style.rich_style)
            )
        strip = Strip(
            self._apply_link_style(widget, segments),
            content.cell_length + pad_left + pad_right,
        )
        return strip

    def _apply_link_style(
        self, widget: Widget, segments: list[Segment]
    ) -> list[Segment]:
        link_style = widget.link_style
        _Segment = Segment
        segments = [
            _Segment(
                text,
                (
                    style
                    if style._meta is None
                    else (style + link_style if "@click" in style.meta else style)
                ),
                control,
            )
            for text, style, control in segments
            if style is not None
        ]
        return segments


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
    content = content.stylize(
        Style(Color.parse("rgb(50,50,80)"), Color.parse("rgba(255,255,255,0.7)"))
    )

    content = content.highlight_regex(
        "F..r", Style(background=Color.parse("rgba(255, 255, 255, 0.3)"))
    )

    content = content.highlight_regex(
        "is", Style(background=Color.parse("rgba(20, 255, 255, 0.3)"))
    )

    content = content.highlight_regex(
        "the", Style(background=Color.parse("rgba(255, 20, 255, 0.3)"))
    )

    content = content.highlight_regex(
        "will", Style(background=Color.parse("rgba(255, 255, 20, 0.3)"))
    )

    lines = content._wrap_and_format(40, align="full")
    print(lines)
    print("x" * 40)
    for line in lines:
        segments = Segments(line.render_segments(ANSI_DEFAULT, end="\n"))
        print(segments)
