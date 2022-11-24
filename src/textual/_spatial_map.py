from __future__ import annotations

from collections import defaultdict
from itertools import product
from operator import attrgetter
from typing import Iterable, Sequence

from ._layout import WidgetPlacement
from .geometry import Region, Spacing
from ._partition import partition
from ._profile import timer


class SpatialMap:
    """An object to return WidgetPlacements within a given region.

    The widget area is split in to a regular grid of buckets. Each placement is assigned to
    any bucket it overlaps, which may be 1 or more buckets.

    The `get_placements` function will calculate which buckets overlap the screen area, and combine
    the placements from those buckets. This generally means that widgets that aren't overlapping or
    near the screen area can be quickly discarded. The result will typically be a superset of visible
    placements, which can then be filtered normally.

    """

    def __init__(
        self,
        placements: Sequence[WidgetPlacement],
        *,
        block_width: int = 40,
        block_height: int = 20,
    ) -> None:
        self._placements = placements
        self._total_region = Region()
        self._block_width = block_width
        self._block_height = block_height
        self._fixed: list[WidgetPlacement] = []
        self._map: defaultdict[tuple[int, int], list[WidgetPlacement]] | None = None

        self.placement_map = self._build_placements(placements)

    def __iter__(self) -> Iterable[WidgetPlacement]:
        yield from self._placements

    def __reversed__(self) -> Iterable[WidgetPlacement]:
        yield from reversed(self._placements)

    def _build_placements(
        self, placements: Iterable[WidgetPlacement]
    ) -> defaultdict[tuple[int, int], list[WidgetPlacement]]:
        """Add placements to map.

        Args:
            placements (Iterable[WidgetPlacement]): A number of placements.
        """
        map: defaultdict[tuple[int, int], list[WidgetPlacement]] = defaultdict(list)
        get_bucket = map.__getitem__

        block_width = self._block_width
        block_height = self._block_height

        self.total_region = Region.from_union(
            [
                placement.region.grow(placement.margin)
                for placement in placements
                if not placement.fixed
            ]
        )

        placements, self._fixed = partition(attrgetter("fixed"), placements)

        for placement in placements:
            x1, y1, width, height = placement.region
            x2 = x1 + width
            y2 = y1 + height
            for coord in product(
                range(x1 // block_width, x2 // block_width + 1),
                range(y1 // block_height, y2 // block_height + 1),
            ):
                get_bucket(coord).append(placement)
        return map

    def get_placements(self, screen_region: Region) -> list[WidgetPlacement]:
        """Get placements that may overlap a given region. There may be false positives,
        but no false negatives.

        Args:
            region (Region): Container region.

        Returns:
            Iterable[WidgetPlacement]: A super-set of Widget placements that may be in the screen.
        """
        return [
            placement
            for placement in self._placements
            if screen_region.overlaps(placement.region)
        ]
        x1, y1, width, height = screen_region
        x2 = x1 + width
        y2 = y1 + height
        block_width = self._block_width
        block_height = self._block_height

        placements: set[WidgetPlacement] = set()
        extend_placements = placements.update
        map = self.placement_map
        map_get = map.get

        overlaps_screen = screen_region.overlaps

        for coord in product(
            range(x1 // block_width, x2 // block_width + 1),
            range(y1 // block_height, y2 // block_height + 1),
        ):
            block_placements = map_get(coord)
            if block_placements is not None:
                extend_placements(block_placements)

        _placements = [
            placement
            for placement in self._placements
            if placement in placements and not placement.fixed
        ]

        visible_placements = self._fixed + [
            placement for placement in _placements if overlaps_screen(placement.region)
        ]
        return visible_placements
