from rich.color import Color as RichColor
from rich.color import ColorType
from rich.segment import Segment
from rich.style import Style
from rich.terminal_theme import MONOKAI

from textual.color import Color
from textual.filter import ANSIToTruecolor


def test_ansi_to_truecolor_8_bit_dim():
    """Test that converting an 8-bit color with dim doesn't crash.

    Regression test for https://github.com/Textualize/textual/issues/5946

    """
    # Given
    ansi_filter = ANSIToTruecolor(MONOKAI)
    test_color = RichColor("color(253)", ColorType.EIGHT_BIT, number=253)
    test_style = Style(color=test_color, dim=True)
    segments = [Segment("This should not crash", style=test_style)]
    background_color = Color(0, 0, 0)

    # When
    # This line will crash if the bug is present
    new_segments = ansi_filter.apply(segments, background_color)

    # Then
    assert new_segments is not None
