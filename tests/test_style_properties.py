from textual.color import Color
from textual.css.styles import Styles


def test_box_normalization():
    """Check that none or hidden is normalized to empty string."""
    styles = Styles()
    styles.border_left = ("none", "red")
    assert styles.border_left == ("", Color.parse("red"))
