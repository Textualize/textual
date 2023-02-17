from textual._spatial_map import SpatialMap
from textual.geometry import Region


def test_region_to_grid():
    spatial_map = SpatialMap()

    assert list(spatial_map._region_to_grid(Region(0, 0, 10, 10))) == [(0, 0)]
