from __future__ import annotations

from itertools import chain
from typing import Iterator, Iterable, Sequence

import rich.repr
from rich.cells import cell_len, set_cell_size
from rich.segment import Segment
from rich.style import Style

from ._filter import LineFilter
from ._segment_tools import line_crop

from ._profile import timer


@rich.repr.auto
class Strip:
    __slots__ = ["_segments", "_cell_length", "_divide_cache"]

    def __init__(
        self, segments: Iterable[Segment], cell_length: int | None = None
    ) -> None:
        self._segments = list(segments)
        self._cell_length = cell_length
        self._divide_cache: dict[tuple[int], list[Strip]] = {}

    def __rich_repr__(self) -> rich.repr.Result:
        yield self._segments
        yield self.cell_length

    @property
    def cell_length(self) -> int:
        """Get the number of cells required to render this object."""
        # Done on demand and cached, as this is an O(n) operation
        if self._cell_length is None:
            self._cell_length = Segment.get_line_length(self._segments)
        return self._cell_length

    @classmethod
    def join(cls, strips: Iterable[Strip | None]) -> Strip:

        segments: list[list[Segment]] = []
        add_segments = segments.append
        total_cell_length = 0
        for strip in strips:
            if strip is None:
                continue
            total_cell_length += strip.cell_length
            add_segments(strip._segments)
        strip = cls(chain.from_iterable(segments), total_cell_length)
        return strip

    def __bool__(self) -> bool:
        return bool(self._segments)

    def __iter__(self) -> Iterator[Segment]:
        return iter(self._segments)

    def __len__(self) -> int:
        return len(self._segments)

    def __eq__(self, strip: Strip) -> bool:
        return (
            self._segments == strip._segments and self.cell_length == strip.cell_length
        )

    def adjust_line_length(self, cell_length: int, style: Style | None) -> Strip:

        new_line: list[Segment]
        line = self._segments
        current_cell_length = self.cell_length

        _Segment = Segment

        if current_cell_length < cell_length:
            new_line = line + [
                _Segment(" " * (cell_length - current_cell_length), style)
            ]

        elif current_cell_length > cell_length:
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
            return self

        return Strip(new_line, cell_length)

    def simplify(self) -> Strip:
        line = Strip(
            Segment.simplify(self._segments),
            self._cell_length,
        )
        return line

    def apply_filter(self, filter: LineFilter) -> Strip:
        return Strip(filter.filter(self._segments), self._cell_length)

    def style_links(self, link_id: str, link_style: Style) -> Strip:
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
        _cell_len = cell_len
        pos = 0
        output_segments: list[Segment] = []
        add_segment = output_segments.append
        iter_segments = iter(self._segments)
        segment: Segment | None = None
        for segment in iter_segments:
            end_pos = pos + _cell_len(segment.text)
            if end_pos > start:
                segment = segment.split_cells(start - pos)[1]
                break
            pos = end_pos
        else:
            return Strip([], 0)

        if end >= self.cell_length:
            # The end crop is the end of the segments, so we can collect all remaining segments
            if segment:
                add_segment(segment)
            output_segments.extend(iter_segments)
            return Strip(output_segments, self.cell_length - start)

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
        return Strip(output_segments, end - start)

    def divide(self, cuts: Iterable[int]) -> list[Strip]:

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
