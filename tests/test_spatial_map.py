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
            Region(10, 10, 10, 10),
            [
                (1, 1),
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

    assert list(spatial_map._region_to_grid_coordinates(region)) == grid


def test_get_values_in_region() -> None:
    spatial_map: SpatialMap[str] = SpatialMap(20, 10)

    spatial_map.insert(
        [
            (Region(10, 5, 5, 5), False, False, "foo"),
            (Region(5, 20, 5, 5), False, False, "bar"),
            (Region(0, 0, 40, 1), True, False, "title"),
        ]
    )

    assert spatial_map.get_values_in_region(Region(0, 0, 10, 5)) == [
        "title",
        "foo",
    ]
    assert spatial_map.get_values_in_region(Region(0, 1, 10, 5)) == ["title", "foo"]
    assert spatial_map.get_values_in_region(Region(0, 10, 10, 5)) == ["title"]
    assert spatial_map.get_values_in_region(Region(0, 20, 10, 5)) == ["title", "bar"]
    assert spatial_map.get_values_in_region(Region(5, 5, 50, 50)) == [
        "title",
        "foo",
        "bar",
    ]
