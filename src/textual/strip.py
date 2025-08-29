"""
This module contains the `Strip` class and related objects.

A `Strip` contains the result of rendering a widget.
See [Line API](/guide/widgets#line-api) for how to use Strips.
"""

from __future__ import annotations

from typing import Any, Iterable, Iterator, Sequence

import rich.repr
from rich.cells import cell_len, set_cell_size
from rich.console import Console, ConsoleOptions, RenderResult
from rich.measure import Measurement
from rich.segment import Segment
from rich.style import Style, StyleType

from textual._segment_tools import index_to_cell_position, line_pad
from textual.cache import FIFOCache
from textual.color import Color
from textual.css.types import AlignHorizontal, AlignVertical
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
    """A renderable which renders a list of strips into lines."""

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
        "_offsets_cache",
        "_link_ids",
        "_cell_count",
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
        self._offsets_cache: FIFOCache[tuple[int, int], Strip] = FIFOCache(4)
        self._render_cache: str | None = None
        self._link_ids: set[str] | None = None
        self._cell_count: int | None = None

    def __rich_repr__(self) -> rich.repr.Result:
        try:
            yield self._segments
            yield self.cell_length
        except AttributeError:
            pass

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

    @classmethod
    def align(
        cls,
        strips: list[Strip],
        style: Style,
        width: int,
        height: int | None,
        horizontal: AlignHorizontal,
        vertical: AlignVertical,
    ) -> Iterable[Strip]:
        """Align a list of strips on both axis.

        Args:
            strips: A list of strips, such as from a render.
            style: The Rich style of additional space.
            width: Width of container.
            height: Height of container.
            horizontal: Horizontal alignment method.
            vertical: Vertical alignment method.

        Returns:
            An iterable of strips, with additional padding.

        """
        if not strips:
            return
        line_lengths = [strip.cell_length for strip in strips]
        shape_width = max(line_lengths)
        shape_height = len(line_lengths)

        def blank_lines(count: int) -> Iterable[Strip]:
            """Create blank lines.

            Args:
                count: Desired number of blank lines.

            Returns:
                An iterable of blank lines.
            """
            blank = cls([Segment(" " * width, style)], width)
            for _ in range(count):
                yield blank

        top_blank_lines = bottom_blank_lines = 0
        if height is not None:
            vertical_excess_space = max(0, height - shape_height)

            if vertical == "top":
                bottom_blank_lines = vertical_excess_space
            elif vertical == "middle":
                top_blank_lines = vertical_excess_space // 2
                bottom_blank_lines = vertical_excess_space - top_blank_lines
            elif vertical == "bottom":
                top_blank_lines = vertical_excess_space

            if top_blank_lines:
                yield from blank_lines(top_blank_lines)

        if horizontal == "left":
            for strip in strips:
                if strip.cell_length == width:
                    yield strip
                else:
                    yield Strip(
                        line_pad(strip._segments, 0, width - strip.cell_length, style),
                        width,
                    )
        elif horizontal == "center":
            left_space = max(0, width - shape_width) // 2
            for strip in strips:
                if strip.cell_length == width:
                    yield strip
                else:
                    yield Strip(
                        line_pad(
                            strip._segments,
                            left_space,
                            width - strip.cell_length - left_space,
                            style,
                        ),
                        width,
                    )

        elif horizontal == "right":
            for strip in strips:
                if strip.cell_length == width:
                    yield strip
                else:
                    yield cls(
                        line_pad(strip._segments, width - strip.cell_length, 0, style),
                        width,
                    )

        if bottom_blank_lines:
            yield from blank_lines(bottom_blank_lines)

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
        """Join a number of strips into one.

        Args:
            strips: An iterable of Strips.

        Returns:
            A new combined strip.
        """
        join_strips = [strip for strip in strips if strip is not None]
        segments = [segment for strip in join_strips for segment in strip._segments]
        cell_length: int | None = None
        if any([strip._cell_length is None for strip in join_strips]):
            cell_length = None
        else:
            cell_length = sum([strip._cell_length or 0 for strip in join_strips])
        return cls(segments, cell_length)

    def __add__(self, other: Strip) -> Strip:
        return Strip.join([self, other])

    def __bool__(self) -> bool:
        return not not self._segments  # faster than bool(...)

    def __iter__(self) -> Iterator[Segment]:
        return iter(self._segments)

    def __reversed__(self) -> Iterator[Segment]:
        return reversed(self._segments)

    def __len__(self) -> int:
        return len(self._segments)

    def __eq__(self, strip: object) -> bool:
        return isinstance(strip, Strip) and (self._segments == strip._segments)

    def __getitem__(self, index: int | slice) -> Strip:
        if isinstance(index, int):
            index = slice(index, index + 1)
        return self.crop(
            index.start, self.cell_count if index.stop is None else index.stop
        )

    @property
    def cell_count(self) -> int:
        """Number of cells in the strip"""
        if self._cell_count is None:
            self._cell_count = sum(len(segment.text) for segment in self._segments)
        return self._cell_count

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

        if self.cell_length == cell_length:
            return self

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
        """Simplify the segments (join segments with same style).

        Returns:
            New strip.
        """
        line = Strip(
            Segment.simplify(self._segments),
            self._cell_length,
        )
        return line

    def discard_meta(self) -> Strip:
        """Remove all meta from segments.

        Returns:
            New strip.
        """

        def remove_meta_from_segment(segment: Segment) -> Segment:
            """Build a Segment with no meta.

            Args:
                segment: Segment.

            Returns:
                Segment, sans meta.
            """
            text, style, control = segment
            if style is None:
                return segment
            style = style.copy()
            style._meta = None
            return Segment(text, style, control)

        return Strip(
            [remove_meta_from_segment(segment) for segment in self._segments],
            self._cell_length,
        )

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
        """Divide the strip into multiple smaller strips by cutting at given (cell) indices.

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

    def apply_meta(self, meta: dict[str, Any]) -> Strip:
        """Apply meta to all segments.

        Args:
            meta: A dict of meta information.

        Returns:
            A new strip.

        """
        meta_style = Style.from_meta(meta)
        return self.apply_style(meta_style)

    def _apply_link_style(self, link_style: Style) -> Strip:
        segments = self._segments
        _Segment = Segment
        segments = [
            (
                _Segment(
                    text,
                    (
                        style
                        if style._meta is None
                        else (style + link_style if "@click" in style.meta else style)
                    ),
                    control,
                )
                if style
                else _Segment(text)
            )
            for text, style, control in segments
        ]
        return Strip(segments, self._cell_length)

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

    def crop_pad(self, cell_length: int, left: int, right: int, style: Style) -> Strip:
        """Crop the strip to `cell_length`, and add optional padding.

        Args:
            cell_length: Cell length of strip prior to padding.
            left: Additional padding on the left.
            right: Additional padding on the right.
            style: Style of any padding.

        Returns:
            Cropped and padded strip.
        """
        if cell_length != self.cell_length:
            strip = self.adjust_cell_length(cell_length, style)
        else:
            strip = self
        if not (left or right):
            return strip
        segments = strip._segments.copy()
        if left:
            segments.insert(0, Segment(" " * left, style))
        if right:
            segments.append(Segment(" " * right, style))
        return Strip(segments, cell_length + left + right)

    def text_align(self, width: int, align: AlignHorizontal) -> Strip:
        if align == "left":
            if self.cell_length == width:
                return self
            else:
                return Strip(
                    line_pad(self._segments, 0, width - self.cell_length, Style.null()),
                    width,
                )
        elif align == "center":
            left_space = max(0, width - self.cell_length) // 2

            if self.cell_length == width:
                return self
            else:
                return Strip(
                    line_pad(
                        self._segments,
                        left_space,
                        width - self.cell_length - left_space,
                        Style.null(),
                    ),
                    width,
                )

        elif align == "right":
            if self.cell_length == width:
                return self
            else:
                return Strip(
                    line_pad(self._segments, width - self.cell_length, 0, Style.null()),
                    width,
                )

    def apply_offsets(self, x: int, y: int) -> Strip:
        """Apply offsets used in text selection.

        Args:
            x: Offset on X axis (column).
            y: Offset on Y axis (row).

        Returns:
            New strip.
        """
        cache_key = (x, y)
        if (cached_strip := self._offsets_cache.get(cache_key)) is not None:
            return cached_strip
        segments = self._segments
        strip_segments: list[Segment] = []
        for segment in segments:
            text, style, _ = segment
            offset_style = Style.from_meta({"offset": (x, y)})
            strip_segments.append(
                Segment(text, style + offset_style if style else offset_style)
            )
            x += len(segment.text)
        strip = Strip(strip_segments, self._cell_length)
        self._offsets_cache[cache_key] = strip
        return strip
