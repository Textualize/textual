from textual._compositor import Compositor
from textual.geometry import Region


def test_regions_to_ranges_no_regions():
    assert list(Compositor._regions_to_spans([])) == []


def test_regions_to_ranges_single_region():
    regions = [Region(0, 0, 3, 2)]
    assert list(Compositor._regions_to_spans(regions)) == [
        (0, 0, 3),
        (1, 0, 3),
    ]


def test_regions_to_ranges_partially_overlapping_regions():
    regions = [Region(0, 0, 2, 2), Region(1, 1, 2, 2)]
    assert list(Compositor._regions_to_spans(regions)) == [
        (0, 0, 2),
        (1, 0, 3),
        (2, 1, 3),
    ]


def test_regions_to_ranges_fully_overlapping_regions():
    regions = [Region(1, 1, 3, 3), Region(2, 2, 1, 1), Region(0, 2, 3, 1)]
    assert list(Compositor._regions_to_spans(regions)) == [
        (1, 1, 4),
        (2, 0, 4),
        (3, 1, 4),
    ]


def test_regions_to_ranges_disjoint_regions_different_lines():
    regions = [Region(0, 0, 2, 1), Region(2, 2, 2, 1)]
    assert list(Compositor._regions_to_spans(regions)) == [(0, 0, 2), (2, 2, 4)]


def test_regions_to_ranges_disjoint_regions_same_line():
    regions = [Region(0, 0, 1, 2), Region(2, 0, 1, 1)]
    assert list(Compositor._regions_to_spans(regions)) == [
        (0, 0, 1),
        (0, 2, 3),
        (1, 0, 1),
    ]


def test_regions_to_ranges_directly_adjacent_ranges_merged():
    regions = [Region(0, 0, 1, 2), Region(1, 0, 1, 2)]
    assert list(Compositor._regions_to_spans(regions)) == [
        (0, 0, 2),
        (1, 0, 2),
    ]
