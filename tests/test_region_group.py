from textual._region_group import RegionGroup, InlineRange
from textual.geometry import Region


def test_inline_ranges_no_regions():
    assert list(RegionGroup([]).inline_ranges()) == []


def test_inline_ranges_single_region():
    regions = [Region(0, 0, 3, 2)]
    assert list(RegionGroup(regions).inline_ranges()) == [InlineRange(0, 0, 2), InlineRange(1, 0, 2)]


def test_inline_ranges_partially_overlapping_regions():
    regions = [Region(0, 0, 2, 2), Region(1, 1, 2, 2)]
    assert list(RegionGroup(regions).inline_ranges()) == [
        InlineRange(0, 0, 1), InlineRange(1, 0, 2), InlineRange(2, 1, 2),
    ]


def test_inline_ranges_fully_overlapping_regions():
    regions = [Region(1, 1, 3, 3), Region(2, 2, 1, 1), Region(0, 2, 3, 1)]
    assert list(RegionGroup(regions).inline_ranges()) == [
        InlineRange(1, 1, 3), InlineRange(2, 0, 3), InlineRange(3, 1, 3)
    ]


def test_inline_ranges_disjoint_regions_different_lines():
    regions = [Region(0, 0, 2, 1), Region(2, 2, 2, 1)]
    assert list(RegionGroup(regions).inline_ranges()) == [InlineRange(0, 0, 1), InlineRange(2, 2, 3)]


def test_inline_ranges_disjoint_regions_same_line():
    regions = [Region(0, 0, 1, 2), Region(2, 0, 1, 1)]
    assert list(RegionGroup(regions).inline_ranges()) == [
        InlineRange(0, 0, 0), InlineRange(0, 2, 2), InlineRange(1, 0, 0)
    ]


def test_inline_ranges_directly_adjacent_ranges_merged():
    regions = [Region(0, 0, 1, 2), Region(1, 0, 1, 2)]
    assert list(RegionGroup(regions).inline_ranges()) == [
        InlineRange(0, 0, 1), InlineRange(1, 0, 1)
    ]
