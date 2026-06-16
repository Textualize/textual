import pytest

from textual._auto_scroll import get_auto_scroll_regions
from textual.geometry import Region


@pytest.mark.parametrize(
    "region, lines, expected",
    [
        # Simple case
        (
            Region(0, 0, 100, 20),
            1,
            (Region(0, 0, 100, 1), Region(0, 19, 100, 1)),
        ),
        # Simple case, more lines
        (
            Region(0, 0, 100, 20),
            3,
            (Region(0, 0, 100, 3), Region(0, 17, 100, 3)),
        ),
        # Potentially overlapping case
        (
            Region(0, 0, 100, 5),
            3,
            (Region(0, 0, 100, 2), Region(0, 2, 100, 3)),
        ),
        # Gross overlapping case, scroll zones should still occupy half
        (
            Region(0, 0, 100, 5),
            5,
            (Region(0, 0, 100, 2), Region(0, 2, 100, 3)),
        ),
    ],
)
def test_auto_scroll_regions(
    region: Region, lines: int, expected: tuple[Region, Region]
):
    """Test calculation of auto scrolling select zones."""
    print(region, lines)
    result = get_auto_scroll_regions(region, lines)
    print(result)
    assert result == expected
