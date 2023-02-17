import pytest

from textual._spatial_map import SpatialMap
from textual.geometry import Region


@pytest.mark.parametrize(
    "region,grid",
    [
        (
            Region(0, 0, 10, 10),
            [
                (0, 0),
            ],
        ),
        (
            Region(0, 0, 11, 11),
            [(0, 0), (0, 1), (1, 0), (1, 1)],
        ),
        (
            Region(5, 5, 15, 3),
            [(0, 0), (1, 0)],
        ),
        (
            Region(5, 5, 2, 15),
            [(0, 0), (0, 1)],
        ),
    ],
)
def test_region_to_grid(region, grid):
    spatial_map = SpatialMap(10, 10)

    assert list(spatial_map._region_to_grid(region)) == grid
