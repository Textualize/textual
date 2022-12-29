from __future__ import annotations

from itertools import chain
from typing import Iterable, Iterator

import rich.repr
from rich.cells import cell_len, set_cell_size
from rich.segment import Segment
from rich.style import Style

from ._cache import FIFOCache
from ._filter import LineFilter


@rich.repr.auto
class Strip:
    """Represents a 'strip' (horizontal line) of a Textual Widget.

    A Strip is like an immutable list of Segments. The immutability allows for effective caching.

    Args:
        segments (Iterable[Segment]): An iterable of segments.
        cell_length (int | None, optional): The cell length if known, or None to calculate on demand. Defaults to None.
    """

    __slots__ = [
        "_segments",
        "_cell_length",
        "_divide_cache",
        "_crop_cache",
    ]

    def __init__(
        self, segments: Iterable[Segment], cell_length: int | None = None
    ) -> None:
        self._segments = list(segments)
        self._cell_length = cell_length
        self._divide_cache: FIFOCache[tuple[int, ...], list[Strip]] = FIFOCache(4)
        self._crop_cache: FIFOCache[tuple[int, int], Strip] = FIFOCache(4)

    def __rich_repr__(self) -> rich.repr.Result:
        yield self._segments
        yield self.cell_length

    @classmethod
    def blank(cls, cell_length: int, style: Style | None) -> Strip:
        """Create a blank strip.

        Args:
            cell_length (int): Desired cell length.
            style (Style | None): Style of blank.

        Returns:
            Strip: New strip.
        """
        return cls([Segment(" " * cell_length, style)], cell_length)

    @classmethod
    def from_lines(cls, lines: list[list[Segment]], cell_length: int) -> list[Strip]:
        """Convert lines (lists of segments) to a list of Strips.

        Args:
            lines (list[list[Segment]]): List of lines, where a line is a list of segments.
            cell_length (int): Cell length of lines (must be same).

        Returns:
            list[Strip]: List of strips.
        """
        return [cls(segments, cell_length) for segments in lines]

    @property
    def cell_length(self) -> int:
        """Get the number of cells required to render this object."""
        # Done on demand and cached, as this is an O(n) operation
        if self._cell_length is None:
            self._cell_length = Segment.get_line_length(self._segments)
        return self._cell_length

    @classmethod
    def join(cls, strips: Iterable[Strip | None]) -> Strip:
        """Join a number of strips in to one.

        Args:
            strips (Iterable[Strip]): An iterable of Strips.

        Returns:
            Strip: A new combined strip.
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
        return bool(self._segments)

    def __iter__(self) -> Iterator[Segment]:
        return iter(self._segments)

    def __reversed__(self) -> Iterator[Segment]:
        return reversed(self._segments)

    def __len__(self) -> int:
        return len(self._segments)

    def __eq__(self, strip: Strip) -> bool:
        return (
            self._segments == strip._segments and self.cell_length == strip.cell_length
        )

    def adjust_cell_length(self, cell_length: int, style: Style | None = None) -> Strip:
        """Adjust the cell length, possibly truncating or extending.

        Args:
            cell_length (int): New desired cell length.
            style (Style | None): Style when extending, or `None`. Defaults to `None`.

        Returns:
            Strip: A new strip with the supplied cell length.
        """

        new_line: list[Segment]
        line = self._segments
        current_cell_length = self.cell_length

        _Segment = Segment

        if current_cell_length < cell_length:
            # Cell length is larger, so pad with spaces.
            new_line = line + [
                _Segment(" " * (cell_length - current_cell_length), style)
            ]

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
        else:
            # Strip is already the required cell length, so return self.
            return self

        return Strip(new_line, cell_length)

    def simplify(self) -> Strip:
        """Simplify the segments (join segments with same style)

        Returns:
            Strip: New strip.
        """
        line = Strip(
            Segment.simplify(self._segments),
            self._cell_length,
        )
        return line

    def apply_filter(self, filter: LineFilter) -> Strip:
        """Apply a filter to all segments in the strip.

        Args:
            filter (LineFilter): A line filter object.

        Returns:
            Strip: A new Strip.
        """
        return Strip(filter.apply(self._segments), self._cell_length)

    def style_links(self, link_id: str, link_style: Style) -> Strip:
        """Apply a style to Segments with the given link_id.

        Args:
            link_id (str): A link id.
            link_style (Style): Style to apply.

        Returns:
            Strip: New strip (or same Strip if no changes).
        """
        _Segment = Segment
        if not any(
            segment.style._link_id == link_id
            for segment in self._segments
            if segment.style
        ):
            return self
        segments = [
            _Segment(
                text,
                (style + link_style if style is not None else None)
                if (style and not style._null and style._link_id == link_id)
                else style,
                control,
            )
            for text, style, control in self._segments
        ]
        return Strip(segments, self._cell_length)

    def crop(self, start: int, end: int) -> Strip:
        """Crop a strip between two cell positions.

        Args:
            start (int): The start cell position (inclusive).
            end (int): The end cell position (exclusive).

        Returns:
            Strip: A new Strip.
        """
        if start == 0 and end == self.cell_length:
            return self
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
        if start > self.cell_length:
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

    def divide(self, cuts: Iterable[int]) -> list[Strip]:
        """Divide the strip in to multiple smaller strips by cutting at given (cell) indices.

        Args:
            cuts (Iterable[int]): An iterable of cell positions as ints.

        Returns:
            list[Strip]: A new list of strips.
        """

        pos = 0
        cache_key = tuple(cuts)
        cached = self._divide_cache.get(cache_key)
        if cached is not None:
            return cached

        strips: list[Strip] = []
        add_strip = strips.append
        for segments, cut in zip(Segment.divide(self._segments, cuts), cuts):
            add_strip(Strip(segments, cut - pos))
            pos += cut

        self._divide_cache[cache_key] = strips
        return strips
