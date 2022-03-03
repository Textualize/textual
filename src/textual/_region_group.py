from __future__ import annotations

from collections import defaultdict
from operator import attrgetter
from typing import NamedTuple, Iterable

from src.textual.geometry import Region


class InlineRange(NamedTuple):
    """Represents a region on a single line."""

    line_index: int
    start: int
    end: int


class RegionGroup:
    """Container which wraps regions and offers utility operations over them.

    Args:
        regions (Iterable[Region]): An iterable of Regions.
    """

    def __init__(self, regions: Iterable[Region]) -> None:
        self.regions = regions

    def inline_ranges(self) -> Iterable[InlineRange]:
        """Converts the regions to non-overlapping horizontal strips, where each strip
        represents the region on a single line. Combining the resulting strips therefore
        results in a shape identical to the combined original regions.

        Returns:
            Iterable[InlineRange]: Yields InlineRange objects representing the content on
                a single line, with overlaps removed.
        """
        if not self.regions:
            return

        inline_ranges: dict[int, list[InlineRange]] = defaultdict(list)
        for region_x, region_y, width, height in self.regions:
            for y in range(region_y, region_y + height):
                inline_ranges[y].append(
                    InlineRange(line_index=y, start=region_x, end=region_x + width - 1)
                )

        for line_index, ranges in inline_ranges.items():
            sorted_ranges = sorted(ranges, key=attrgetter("start"))
            _, start, end = sorted_ranges[0]
            for next_line_index, next_start, next_end in sorted_ranges[1:]:
                if next_start <= end + 1:
                    end = max(end, next_end)
                else:
                    yield InlineRange(line_index, start, end)
                    start = next_start
                    end = next_end
            yield InlineRange(line_index, start, end)
