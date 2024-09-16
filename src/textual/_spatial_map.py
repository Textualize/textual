from __future__ import annotations

from collections import defaultdict
from itertools import product
from typing import Generic, Iterable, TypeVar

from typing_extensions import TypeAlias

from textual.geometry import Region

ValueType = TypeVar("ValueType")
GridCoordinate: TypeAlias = "tuple[int, int]"


class SpatialMap(Generic[ValueType]):
    """A spatial map allows for data to be associated with rectangular regions
    in Euclidean space, and efficiently queried.

    When the SpatialMap is populated, a reference to each value is placed into one or
    more buckets associated with a regular grid that covers 2D space.

    The SpatialMap is able to quickly retrieve the values under a given "window" region
    by combining the values in the grid squares under the visible area.
    """

    def __init__(self, grid_width: int = 100, grid_height: int = 20) -> None:
        """Create a spatial map with the given grid size.

        Args:
            grid_width: Width of a grid square.
            grid_height: Height of a grid square.
        """
        self._grid_size = (grid_width, grid_height)
        self.total_region = Region()
        self._map: defaultdict[GridCoordinate, list[ValueType]] = defaultdict(list)
        self._fixed: list[ValueType] = []

    def _region_to_grid_coordinates(self, region: Region) -> Iterable[GridCoordinate]:
        """Get the grid squares under a region.

        Args:
            region: A region.

        Returns:
            Iterable of grid coordinates (tuple of 2 values).
        """
        # (x1, y1) is the coordinate of the top left cell
        # (x2, y2) is the coordinate of the bottom right cell
        x1, y1, width, height = region
        x2 = x1 + width - 1
        y2 = y1 + height - 1
        grid_width, grid_height = self._grid_size

        return product(
            range(x1 // grid_width, x2 // grid_width + 1),
            range(y1 // grid_height, y2 // grid_height + 1),
        )

    def insert(
        self, regions_and_values: Iterable[tuple[Region, bool, bool, ValueType]]
    ) -> None:
        """Insert values into the Spatial map.

        Values are associated with their region in Euclidean space, and a boolean that
        indicates fixed regions. Fixed regions don't scroll and are always visible.

        Args:
            regions_and_values: An iterable of (REGION, FIXED, OVERLAY, VALUE).
        """
        append_fixed = self._fixed.append
        get_grid_list = self._map.__getitem__
        _region_to_grid = self._region_to_grid_coordinates
        total_region = self.total_region
        for region, fixed, overlay, value in regions_and_values:
            if fixed:
                append_fixed(value)
            else:
                if not overlay:
                    total_region = total_region.union(region)
                for grid in _region_to_grid(region):
                    get_grid_list(grid).append(value)
        self.total_region = total_region

    def get_values_in_region(self, region: Region) -> list[ValueType]:
        """Get a superset of all the values that intersect with a given region.

        Note that this may return false positives.

        Args:
            region: A region.

        Returns:
            Values under the region.
        """
        results: list[ValueType] = self._fixed.copy()
        add_results = results.extend
        get_grid_values = self._map.get
        for grid_coordinate in self._region_to_grid_coordinates(region):
            grid_values = get_grid_values(grid_coordinate)
            if grid_values is not None:
                add_results(grid_values)
        unique_values = list(dict.fromkeys(results))
        return unique_values
