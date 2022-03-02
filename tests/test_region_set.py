from textual._region_set import RegionSet, InlineRange
from textual.geometry import Region


def test_inline_ranges_no_regions():
    assert list(RegionSet([]).inline_ranges()) == []


def test_as_strips_single_region():
    regions = [Region(0, 0, 3, 2)]
    assert list(RegionSet(regions).inline_ranges()) == [InlineRange(0, 0, 2), InlineRange(1, 0, 2)]


def test_as_strips_overlapping_regions():
    regions = [Region(0, 0, 2, 2), Region(1, 1, 2, 2)]
    assert list(RegionSet(regions).inline_ranges()) == [
        InlineRange(0, 0, 1), InlineRange(1, 0, 2), InlineRange(2, 1, 2),
    ]


def test_as_strips_disjoint_regions_different_lines():
    regions = [Region(0, 0, 2, 1), Region(2, 2, 2, 1)]
    assert list(RegionSet(regions).inline_ranges()) == [InlineRange(0, 0, 1), InlineRange(2, 2, 3)]


def test_as_strips_disjoint_regions_same_line():
    regions = [Region(0, 0, 1, 2), Region(2, 0, 1, 1)]
    assert list(RegionSet(regions).inline_ranges()) == [
        InlineRange(0, 0, 0), InlineRange(0, 2, 2), InlineRange(1, 0, 0)
    ]
