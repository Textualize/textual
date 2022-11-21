from __future__ import annotations

from collections import defaultdict
from itertools import product
from typing import Iterable, Mapping

from ._layout import WidgetPlacement
from .geometry import Region


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
        placements: Iterable[WidgetPlacement],
        block_width: int = 80,
        block_height: int = 80,
    ) -> None:
        self._placements = placements
        self._block_width = block_width
        self._block_height = block_height
        self._map: defaultdict[tuple[int, int], list[WidgetPlacement]] | None = None

    @property
    def placement_map(self) -> Mapping[tuple[int, int], list[WidgetPlacement]]:
        """A mapping of block coordinate on to widget placement.

        Returns:
            Mapping[tuple[int, int], list[WidgetPlacement]]: Mapping.
        """
        if self._map is None:
            self._map = self._build_placements(self._placements)
            return self._map
        return self._map

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

    def get_placements(self, screen_region: Region) -> Iterable[WidgetPlacement]:
        """Get placements that may overlap a given region. There may be false positives,
        but no false negatives.

        Args:
            region (Region): Container region.

        Returns:
            set[WidgetPlacement]: Set of Widget placements.
        """
        x1, y1, width, height = screen_region
        x2 = x1 + width
        y2 = y1 + height
        block_width = self._block_width
        block_height = self._block_height

        placements: set[WidgetPlacement] = set()
        extend_placements = placements.update
        map = self.placement_map
        map_get = map.get

        for coord in product(
            range(x1 // block_width, x2 // block_width + 1),
            range(y1 // block_height, y2 // block_height + 1),
        ):
            block_placements = map_get(coord)
            if block_placements is not None:
                extend_placements(block_placements)

        return placements
