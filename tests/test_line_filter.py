from rich.segment import Segment
from rich.style import Style

from textual.color import Color
from textual.filter import DimFilter


def test_dim_apply():
    """Check dim filter changes color and resets dim attribute."""

    dim_filter = DimFilter()

    segments = [Segment("Hello, World!", Style.parse("dim #ffffff on #0000ff"))]

    dimmed_segments = dim_filter.apply(segments, Color(0, 0, 0))

    expected = [Segment("Hello, World!", Style.parse("not dim #7f7fff on #0000ff"))]

    assert dimmed_segments == expected
