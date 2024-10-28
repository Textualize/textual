"""
This module contains the `Strip` class and related objects.

A `Strip` contains the result of rendering a widget.
See [Line API](/guide/widgets#line-api) for how to use Strips.
"""

from __future__ import annotations

from itertools import chain
from typing import Iterable, Iterator, Sequence

import rich.repr
from rich.cells import cell_len, set_cell_size
from rich.console import Console, ConsoleOptions, RenderResult
from rich.measure import Measurement
from rich.segment import Segment
from rich.style import Style, StyleType

from textual._segment_tools import index_to_cell_position
from textual.cache import FIFOCache
from textual.color import Color
from textual.constants import DEBUG
from textual.filter import LineFilter


def get_line_length(segments: Iterable[Segment]) -> int:
    """Get the line length (total length of all segments).

    Args:
        segments: Iterable of segments.

    Returns:
        Length of line in cells.
    """
    _cell_len = cell_len
    return sum([_cell_len(text) for text, _, control in segments if not control])


class StripRenderable:
    """A renderable which renders a list of strips in to lines."""

    def __init__(self, strips: list[Strip], width: int | None = None) -> None:
        self._strips = strips
        self._width = width

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        new_line = Segment.line()
        for strip in self._strips:
            yield from strip
            yield new_line

    def __rich_measure__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> Measurement:
        if self._width is None:
            width = max(strip.cell_length for strip in self._strips)
        else:
            width = self._width
        return Measurement(width, width)


@rich.repr.auto
class Strip:
    """Represents a 'strip' (horizontal line) of a Textual Widget.

    A Strip is like an immutable list of Segments. The immutability allows for effective caching.

    Args:
        segments: An iterable of segments.
        cell_length: The cell length if known, or None to calculate on demand.
    """

    __slots__ = [
        "_segments",
        "_cell_length",
        "_divide_cache",
        "_crop_cache",
        "_style_cache",
        "_filter_cache",
        "_render_cache",
        "_line_length_cache",
        "_crop_extend_cache",
        "_link_ids",
    ]

    def __init__(
        self, segments: Iterable[Segment], cell_length: int | None = None
    ) -> None:
        self._segments = list(segments)
        self._cell_length = cell_length
        self._divide_cache: FIFOCache[tuple[int, ...], list[Strip]] = FIFOCache(4)
        self._crop_cache: FIFOCache[tuple[int, int], Strip] = FIFOCache(16)
        self._style_cache: FIFOCache[Style, Strip] = FIFOCache(16)
        self._filter_cache: FIFOCache[tuple[LineFilter, Color], Strip] = FIFOCache(4)
        self._line_length_cache: FIFOCache[
            tuple[int, Style | None],
            Strip,
        ] = FIFOCache(4)
        self._crop_extend_cache: FIFOCache[
            tuple[int, int, Style | None],
            Strip,
        ] = FIFOCache(4)
        self._render_cache: str | None = None
        self._link_ids: set[str] | None = None

        if DEBUG and cell_length is not None:
            # If `cell_length` is incorrect, render will be fubar
            assert get_line_length(self._segments) == cell_length

    def __rich_repr__(self) -> rich.repr.Result:
        yield self._segments
        yield self.cell_length

    @property
    def text(self) -> str:
        """Segment text."""
        return "".join(segment.text for segment in self._segments)

    @property
    def link_ids(self) -> set[str]:
        """A set of the link ids in this Strip."""
        if self._link_ids is None:
            self._link_ids = {
                style._link_id for _, style, _ in self._segments if style is not None
            }
        return self._link_ids

    @classmethod
    def blank(cls, cell_length: int, style: StyleType | None = None) -> Strip:
        """Create a blank strip.

        Args:
            cell_length: Desired cell length.
            style: Style of blank.

        Returns:
            New strip.
        """
        segment_style = Style.parse(style) if isinstance(style, str) else style
        return cls([Segment(" " * cell_length, segment_style)], cell_length)

    @classmethod
    def from_lines(
        cls, lines: list[list[Segment]], cell_length: int | None = None
    ) -> list[Strip]:
        """Convert lines (lists of segments) to a list of Strips.

        Args:
            lines: List of lines, where a line is a list of segments.
            cell_length: Cell length of lines (must be same) or None if not known.

        Returns:
            List of strips.
        """
        return [cls(segments, cell_length) for segments in lines]

    def index_to_cell_position(self, index: int) -> int:
        """Given a character index, return the cell position of that character.
        This is the sum of the cell lengths of all the characters *before* the character
        at `index`.

        Args:
            index: The index to convert.

        Returns:
            The cell position of the character at `index`.
        """
        return index_to_cell_position(self._segments, index)

    @property
    def cell_length(self) -> int:
        """Get the number of cells required to render this object."""
        # Done on demand and cached, as this is an O(n) operation
        if self._cell_length is None:
            self._cell_length = get_line_length(self._segments)
        return self._cell_length

    @classmethod
    def join(cls, strips: Iterable[Strip | None]) -> Strip:
        """Join a number of strips in to one.

        Args:
            strips: An iterable of Strips.

        Returns:
            A new combined strip.
        """

        segments: list[list[Segment]] = []
        add_segments = segments.append
        total_cell_length = 0
        for strip in strips:
            if strip is not None:
                total_cell_length += strip.cell_length
                add_segments(strip._segments)
        strip = cls(chain.from_iterable(segments), total_cell_length)
        return strip

    def __bool__(self) -> bool:
        return not not self._segments  # faster than bool(...)

    def __iter__(self) -> Iterator[Segment]:
        return iter(self._segments)

    def __reversed__(self) -> Iterator[Segment]:
        return reversed(self._segments)

    def __len__(self) -> int:
        return len(self._segments)

    def __eq__(self, strip: object) -> bool:
        return isinstance(strip, Strip) and (
            self._segments == strip._segments and self.cell_length == strip.cell_length
        )

    def extend_cell_length(self, cell_length: int, style: Style | None = None) -> Strip:
        """Extend the cell length if it is less than the given value.

        Args:
            cell_length: Required minimum cell length.
            style: Style for padding if the cell length is extended.

        Returns:
            A new Strip.
        """
        if self.cell_length < cell_length:
            missing_space = cell_length - self.cell_length
            segments = self._segments + [Segment(" " * missing_space, style)]
            return Strip(segments, cell_length)
        else:
            return self

    def adjust_cell_length(self, cell_length: int, style: Style | None = None) -> Strip:
        """Adjust the cell length, possibly truncating or extending.

        Args:
            cell_length: New desired cell length.
            style: Style when extending, or `None`.

        Returns:
            A new strip with the supplied cell length.
        """

        cache_key = (cell_length, style)
        cached_strip = self._line_length_cache.get(cache_key)
        if cached_strip is not None:
            return cached_strip

        new_line: list[Segment]
        line = self._segments
        current_cell_length = self.cell_length

        _Segment = Segment

        if current_cell_length < cell_length:
            # Cell length is larger, so pad with spaces.
            new_line = line + [
                _Segment(" " * (cell_length - current_cell_length), style)
            ]
            strip = Strip(new_line, cell_length)

        elif current_cell_length > cell_length:
            # Cell length is shorter so we need to truncate.
            new_line = []
            append = new_line.append
            line_length = 0
            for segment in line:
                segment_length = segment.cell_length
                if line_length + segment_length < cell_length:
                    append(segment)
                    line_length += segment_length
                else:
                    text, segment_style, _ = segment
                    text = set_cell_size(text, cell_length - line_length)
                    append(_Segment(text, segment_style))
                    break
            strip = Strip(new_line, cell_length)
        else:
            # Strip is already the required cell length, so return self.
            strip = self

        self._line_length_cache[cache_key] = strip

        return strip

    def simplify(self) -> Strip:
        """Simplify the segments (join segments with same style)

        Returns:
            New strip.
        """
        line = Strip(
            Segment.simplify(self._segments),
            self._cell_length,
        )
        return line

    def apply_filter(self, filter: LineFilter, background: Color) -> Strip:
        """Apply a filter to all segments in the strip.

        Args:
            filter: A line filter object.

        Returns:
            A new Strip.
        """
        cached_strip = self._filter_cache.get((filter, background))
        if cached_strip is None:
            cached_strip = Strip(
                filter.apply(self._segments, background), self._cell_length
            )
            self._filter_cache[(filter, background)] = cached_strip
        return cached_strip

    def style_links(self, link_id: str, link_style: Style) -> Strip:
        """Apply a style to Segments with the given link_id.

        Args:
            link_id: A link id.
            link_style: Style to apply.

        Returns:
            New strip (or same Strip if no changes).
        """

        _Segment = Segment
        if link_id not in self.link_ids:
            return self
        segments = [
            _Segment(
                text,
                (
                    (style + link_style if style is not None else None)
                    if (style and not style._null and style._link_id == link_id)
                    else style
                ),
                control,
            )
            for text, style, control in self._segments
        ]
        return Strip(segments, self._cell_length)

    def crop_extend(self, start: int, end: int, style: Style | None) -> Strip:
        """Crop between two points, extending the length if required.

        Args:
            start: Start offset of crop.
            end: End offset of crop.
            style: Style of additional padding.

        Returns:
            New cropped Strip.
        """
        cache_key = (start, end, style)
        cached_result = self._crop_extend_cache.get(cache_key)
        if cached_result is not None:
            return cached_result
        strip = self.extend_cell_length(end, style).crop(start, end)
        self._crop_extend_cache[cache_key] = strip
        return strip

    def crop(self, start: int, end: int | None = None) -> Strip:
        """Crop a strip between two cell positions.

        Args:
            start: The start cell position (inclusive).
            end: The end cell position (exclusive).

        Returns:
            A new Strip.
        """

        start = max(0, start)
        end = self.cell_length if end is None else min(self.cell_length, end)
        if start == 0 and end == self.cell_length:
            return self
        if end <= start:
            return Strip([], 0)
        cache_key = (start, end)
        cached = self._crop_cache.get(cache_key)
        if cached is not None:
            return cached
        _cell_len = cell_len
        pos = 0
        output_segments: list[Segment] = []
        add_segment = output_segments.append
        iter_segments = iter(self._segments)
        segment: Segment | None = None
        if start >= self.cell_length:
            strip = Strip([], 0)
        else:
            for segment in iter_segments:
                end_pos = pos + _cell_len(segment.text)
                if end_pos > start:
                    segment = segment.split_cells(start - pos)[1]
                    break
                pos = end_pos

            if end >= self.cell_length:
                # The end crop is the end of the segments, so we can collect all remaining segments
                if segment:
                    add_segment(segment)
                output_segments.extend(iter_segments)
                strip = Strip(output_segments, self.cell_length - start)
            else:
                pos = start
                while segment is not None:
                    end_pos = pos + _cell_len(segment.text)
                    if end_pos < end:
                        add_segment(segment)
                    else:
                        add_segment(segment.split_cells(end - pos)[0])
                        break
                    pos = end_pos
                    segment = next(iter_segments, None)
                strip = Strip(output_segments, end - start)
        self._crop_cache[cache_key] = strip
        return strip

    def divide(self, cuts: Iterable[int]) -> Sequence[Strip]:
        """Divide the strip in to multiple smaller strips by cutting at given (cell) indices.

        Args:
            cuts: An iterable of cell positions as ints.

        Returns:
            A new list of strips.
        """

        pos = 0
        cell_length = self.cell_length
        cuts = [cut for cut in cuts if cut <= cell_length]
        cache_key = tuple(cuts)
        cached = self._divide_cache.get(cache_key)
        if cached is not None:
            return cached

        strips: list[Strip]
        if cuts == [cell_length]:
            strips = [self]
        else:
            strips = []
            add_strip = strips.append
            for segments, cut in zip(Segment.divide(self._segments, cuts), cuts):
                add_strip(Strip(segments, cut - pos))
                pos = cut

        self._divide_cache[cache_key] = strips
        return strips

    def apply_style(self, style: Style) -> Strip:
        """Apply a style to the Strip.

        Args:
            style: A Rich style.

        Returns:
            A new strip.
        """
        cached = self._style_cache.get(style)
        if cached is not None:
            return cached
        styled_strip = Strip(
            Segment.apply_style(self._segments, style), self.cell_length
        )
        self._style_cache[style] = styled_strip
        return styled_strip

    def render(self, console: Console) -> str:
        """Render the strip into terminal sequences.

        Args:
            console: Console instance.

        Returns:
            Rendered sequences.
        """
        if self._render_cache is None:
            color_system = console._color_system
            render = Style.render
            self._render_cache = "".join(
                [
                    render(style, text, color_system=color_system)
                    for text, style, _ in self._segments
                    if style is not None
                ]
            )
        return self._render_cache
