import pytest

from rich.color import Color as RichColor
from textual.color import Color, ColorPair


@pytest.mark.parametrize(
    "text,expected",
    [
        ("#000000", Color(0, 0, 0, 1.0)),
        ("#ffffff", Color(255, 255, 255, 1.0)),
        ("#FFFFFF", Color(255, 255, 255, 1.0)),
        ("#020304ff", Color(2, 3, 4, 1.0)),
        ("#02030400", Color(2, 3, 4, 0.0)),
        ("#0203040f", Color(2, 3, 4, 0.058823529411764705)),
        ("rgb(0,0,0)", Color(0, 0, 0, 1.0)),
        ("rgb(255,255,255)", Color(255, 255, 255, 1.0)),
        ("rgba(255,255,255,1)", Color(255, 255, 255, 1.0)),
        ("rgb(2,3,4)", Color(2, 3, 4, 1.0)),
        ("rgba(2,3,4,1.0)", Color(2, 3, 4, 1.0)),
        ("rgba(2,3,4,0.058823529411764705)", Color(2, 3, 4, 0.058823529411764705)),
    ],
)
def test_parse(text, expected):
    assert Color.parse(text) == expected


def test_rich_color():
    """Check conversion to Rich color."""
    assert Color(10, 20, 30, 1.0).rich_color == RichColor.from_rgb(10, 20, 30)


def test_css():
    """Check conversion to CSS style"""
    assert Color(10, 20, 30, 1.0).css == "rgb(10,20,30)"
    assert Color(10, 20, 30, 0.5).css == "rgba(10,20,30,0.5)"


def test_colorpair_style():
    """Test conversion of colorpair to style."""

    # Black on white
    assert (
        str(ColorPair(Color.parse("#000000"), Color.parse("#ffffff")).style)
        == "#000000 on #ffffff"
    )

    # 50% black on white
    assert (
        str(ColorPair(Color.parse("rgba(0,0,0,0.5)"), Color.parse("#ffffff")).style)
        == "#7f7f7f on #ffffff"
    )
