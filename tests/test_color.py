import pytest

from rich.color import Color as RichColor
from rich.text import Text

from textual.color import Color, ColorPair, Lab, lab_to_rgb, rgb_to_lab


def test_rich_color():
    """Check conversion to Rich color."""
    assert Color(10, 20, 30, 1.0).rich_color == RichColor.from_rgb(10, 20, 30)
    assert Color.from_rich_color(RichColor.from_rgb(10, 20, 30)) == Color(
        10, 20, 30, 1.0
    )


def test_rich_color_rich_output():
    assert isinstance(Color(10, 20, 30).__rich__(), Text)


def test_normalized():
    assert Color(255, 128, 64).normalized == pytest.approx((1.0, 128 / 255, 64 / 255))


def test_clamped():
    assert Color(300, 100, -20, 1.5).clamped == Color(255, 100, 0, 1.0)


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


def test_hls():

    red = Color(200, 20, 32)
    print(red.hls)
    assert red.hls == pytest.approx(
        (0.9888888888888889, 0.43137254901960786, 0.818181818181818)
    )
    assert Color.from_hls(
        0.9888888888888889, 0.43137254901960786, 0.818181818181818
    ).normalized == pytest.approx(red.normalized, rel=1e-5)


def test_color_brightness():
    assert Color(255, 255, 255).brightness == 1
    assert Color(0, 0, 0).brightness == 0
    assert Color(127, 127, 127).brightness == pytest.approx(0.49803921568627446)
    assert Color(255, 127, 64).brightness == pytest.approx(0.6199607843137255)


def test_color_hex():
    assert Color(255, 0, 127).hex == "#FF007F"
    assert Color(255, 0, 127, 0.5).hex == "#FF007F7F"


def test_color_css():
    assert Color(255, 0, 127).css == "rgb(255,0,127)"
    assert Color(255, 0, 127, 0.5).css == "rgba(255,0,127,0.5)"


def test_color_with_alpha():
    assert Color(255, 50, 100).with_alpha(0.25) == Color(255, 50, 100, 0.25)


def test_color_blend():
    assert Color(0, 0, 0).blend(Color(255, 255, 255), 0) == Color(0, 0, 0)
    assert Color(0, 0, 0).blend(Color(255, 255, 255), 1.0) == Color(255, 255, 255)
    assert Color(0, 0, 0).blend(Color(255, 255, 255), 0.5) == Color(127, 127, 127)


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
def test_color_parse(text, expected):
    assert Color.parse(text) == expected


def test_color_parse_color():
    # as a convenience, if Color.parse is passed a color object, it will return it
    color = Color(20, 30, 40, 0.5)
    assert Color.parse(color) is color


def test_color_add():
    assert Color(50, 100, 200) + Color(10, 20, 30, 0.9) == Color(14, 28, 47)


# Computed with http://www.easyrgb.com/en/convert.php,
# (r, g, b) values in sRGB to (L*, a*, b*) values in CIE-L*ab.
RGB_LAB_DATA = [
    (10, 23, 73, 10.245, 15.913, -32.672),
    (200, 34, 123, 45.438, 67.750, -8.008),
    (0, 0, 0, 0, 0, 0),
    (255, 255, 255, 100, 0, 0),
]


def test_color_darken():
    assert Color(200, 210, 220).darken(1) == Color(0, 0, 0)
    assert Color(200, 210, 220).darken(-1) == Color(255, 255, 255)
    assert Color(200, 210, 220).darken(0.1) == Color(172, 182, 192)
    assert Color(200, 210, 220).darken(0.5) == Color(71, 80, 88)


def test_color_lighten():
    assert Color(200, 210, 220).lighten(1) == Color(255, 255, 255)
    assert Color(200, 210, 220).lighten(-1) == Color(0, 0, 0)
    assert Color(200, 210, 220).lighten(0.1) == Color(228, 238, 248)


@pytest.mark.parametrize(
    "r, g, b, L_, a_, b_",
    RGB_LAB_DATA,
)
def test_rgb_to_lab(r, g, b, L_, a_, b_):
    """Test conversion from the RGB color space to CIE-L*ab."""
    rgb = Color(r, g, b)
    lab = rgb_to_lab(rgb)
    assert lab.L == pytest.approx(L_, abs=0.1)
    assert lab.a == pytest.approx(a_, abs=0.1)
    assert lab.b == pytest.approx(b_, abs=0.1)


@pytest.mark.parametrize(
    "r, g, b, L_, a_, b_",
    RGB_LAB_DATA,
)
def test_lab_to_rgb(r, g, b, L_, a_, b_):
    """Test conversion from the CIE-L*ab color space to RGB."""

    lab = Lab(L_, a_, b_)
    rgb = lab_to_rgb(lab)
    assert rgb.r == pytest.approx(r, abs=1)
    assert rgb.g == pytest.approx(g, abs=1)
    assert rgb.b == pytest.approx(b, abs=1)


def test_rgb_lab_rgb_roundtrip():
    """Test RGB -> CIE-L*ab -> RGB color conversion roundtripping."""

    for r in range(0, 256, 32):
        for g in range(0, 256, 32):
            for b in range(0, 256, 32):
                c_ = lab_to_rgb(rgb_to_lab(Color(r, g, b)))
                assert c_.r == pytest.approx(r, abs=1)
                assert c_.g == pytest.approx(g, abs=1)
                assert c_.b == pytest.approx(b, abs=1)


def test_color_pair_style():
    pair = ColorPair(Color(220, 220, 220), Color(10, 20, 30))
    assert str(pair.style) == "#dcdcdc on #0a141e"
