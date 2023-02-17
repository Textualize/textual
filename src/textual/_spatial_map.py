from collections import defaultdict
from itertools import product
from typing import Generic, Iterable, TypeVar

from .geometry import Region

ValueType = TypeVar("ValueType")


class SpatialMap(Generic[ValueType]):
    """A spatial map allows for data to be associated with a rectangular regions
    in Euclidean space, and efficiently queried.

    """

    def __init__(self, grid_width: int = 100, grid_height: int = 20) -> None:
        """Create a spatial map with the given grid size.

        Args:
            grid_width: Width of a grid square.
            grid_height: Height of a grid square.
        """
        self._grid_size = (grid_width, grid_height)
        self.total_region = Region()
        self._map: defaultdict[tuple[int, int], list[ValueType]] = defaultdict(list)
        self._fixed: list[ValueType] = []

    def _region_to_grid(self, region: Region) -> Iterable[tuple[int, int]]:
        """Get the grid squares under a region.

        Args:
            region: A region.

        Returns:
            Iterable of grid squares (tuple of 2 values).
        """
        x1, y1, width, height = region
        x2 = x1 + width
        y2 = y1 + height
        grid_width, grid_height = self._grid_size

        return product(
            range(x1 // grid_width, 1 + x2 // grid_width),
            range(y1 // grid_height, 1 + y2 // grid_height),
        )

    def insert(
        self, regions_and_values: Iterable[tuple[Region, bool, ValueType]]
    ) -> None:
        """Insert values in to the Spatial map.

        Args:
            regions_and_values: An iterable of Regions and values.
        """
        append_fixed = self._fixed.append
        get_grid_list = self._map.__getitem__
        _region_to_grid = self._region_to_grid
        total_region = self.total_region
        for region, fixed, value in regions_and_values:
            total_region = total_region.union(region)
            if fixed:
                append_fixed(value)
            else:
                for grid in _region_to_grid(region):
                    get_grid_list(grid).append(value)
        self.total_region = total_region

    def get_values_in_region(self, region: Region) -> list[ValueType]:
        """Get a set of values that are under a given region.

        Note that this may return some false positives.

        Args:
            region: A region.

        Returns:
            A set of values under the region.
        """
        results: list[ValueType] = self._fixed.copy()
        add_results = results.extend
        get_grid_values = self._map.get
        for grid in self._region_to_grid(region):
            grid_values = get_grid_values(grid)
            if grid_values is not None:
                add_results(grid_values)
        unique_values = list(dict.fromkeys(results))
        return unique_values
