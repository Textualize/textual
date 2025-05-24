import pytest
from rich.color import Color as RichColor

from textual.color import Color, Gradient, Lab, lab_to_rgb, rgb_to_lab


def test_rich_color():
    """Check conversion to Rich color."""
    assert Color(10, 20, 30, 1.0).rich_color == RichColor.from_rgb(10, 20, 30)
    assert Color.from_rich_color(RichColor.from_rgb(10, 20, 30)) == Color(
        10, 20, 30, 1.0
    )


def test_normalized():
    assert Color(255, 128, 64).normalized == pytest.approx((1.0, 128 / 255, 64 / 255))


def test_clamped():
    assert Color(300, 100, -20, 1.5).clamped == Color(255, 100, 0, 1.0)


def test_css():
    """Check conversion to CSS style"""
    assert Color(10, 20, 30, 1.0).css == "rgb(10,20,30)"
    assert Color(10, 20, 30, 0.5).css == "rgba(10,20,30,0.5)"
    assert Color(0, 0, 0, 0, ansi=1).css == "ansi_red"
    assert Color(10, 20, 30, 0.5, 0, True).css == "auto 50%"
    assert Color.automatic(70.5).css == "auto 70.5%"


def test_monochrome():
    assert Color(10, 20, 30).monochrome == Color(19, 19, 19)
    assert Color(10, 20, 30, 0.5).monochrome == Color(19, 19, 19, 0.5)
    assert Color(255, 255, 255).monochrome == Color(255, 255, 255)
    assert Color(0, 0, 0).monochrome == Color(0, 0, 0)


def test_rgb():
    assert Color(10, 20, 30, 0.55).rgb == (10, 20, 30)


def test_hsl():
    red = Color(200, 20, 32)
    print(red.hsl)
    assert red.hsl == pytest.approx(
        (0.9888888888888889, 0.818181818181818, 0.43137254901960786)
    )
    assert Color.from_hsl(
        0.9888888888888889, 0.818181818181818, 0.43137254901960786
    ).normalized == pytest.approx(red.normalized, rel=1e-5)
    assert red.hsl.css == "hsl(356,81.8%,43.1%)"


def test_hsv():
    red = Color(200, 20, 32)
    print(red.hsv)
    assert red.hsv == pytest.approx(
        (0.9888888888888889, 0.8999999999999999, 0.7843137254901961)
    )
    assert Color.from_hsv(
        0.9888888888888889, 0.8999999999999999, 0.7843137254901961
    ).normalized == pytest.approx(red.normalized, rel=1e-5)


def test_color_brightness():
    assert Color(255, 255, 255).brightness == 1
    assert Color(0, 0, 0).brightness == 0
    assert Color(127, 127, 127).brightness == pytest.approx(0.49803921568627446)
    assert Color(255, 127, 64).brightness == pytest.approx(0.6199607843137255)


def test_color_hex():
    assert Color(255, 0, 127).hex == "#FF007F"
    assert Color(255, 0, 127, 0.5).hex == "#FF007F7F"


def test_color_hex6():
    assert Color(0, 0, 0).hex6 == "#000000"
    assert Color(255, 255, 255, 0.25).hex6 == "#FFFFFF"
    assert Color(255, 0, 127, 0.5).hex6 == "#FF007F"


def test_color_css():
    assert Color(255, 0, 127).css == "rgb(255,0,127)"
    assert Color(255, 0, 127, 0.5).css == "rgba(255,0,127,0.5)"


def test_color_with_alpha():
    assert Color(255, 50, 100).with_alpha(0.25) == Color(255, 50, 100, 0.25)


def test_multiply_alpha():
    assert Color(100, 100, 100).multiply_alpha(0.5) == Color(100, 100, 100, 0.5)
    assert Color(100, 100, 100, 0.5).multiply_alpha(0.5) == Color(100, 100, 100, 0.25)


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
        ("#fab", Color(255, 170, 187, 1.0)),  # #ffaabb
        ("#fab0", Color(255, 170, 187, 0.0)),  # #ffaabb00
        ("#020304ff", Color(2, 3, 4, 1.0)),
        ("#02030400", Color(2, 3, 4, 0.0)),
        ("#0203040f", Color(2, 3, 4, 0.058823529411764705)),
        ("rgb(0,0,0)", Color(0, 0, 0, 1.0)),
        ("rgb(255,255,255)", Color(255, 255, 255, 1.0)),
        ("rgba(255,255,255,1)", Color(255, 255, 255, 1.0)),
        ("rgb(2,3,4)", Color(2, 3, 4, 1.0)),
        ("rgba(2,3,4,1.0)", Color(2, 3, 4, 1.0)),
        ("rgba(2,3,4,0.058823529411764705)", Color(2, 3, 4, 0.058823529411764705)),
        ("hsl(45,25%,25%)", Color(80, 72, 48)),
        ("hsla(45,25%,25%,0.35)", Color(80, 72, 48, 0.35)),
    ],
)
def test_color_parse(text, expected):
    assert Color.parse(text) == expected


@pytest.mark.parametrize(
    "input,output",
    [
        ("rgb( 300, 300 , 300 )", Color(255, 255, 255)),
        ("rgba( 2 , 3 , 4, 1.0 )", Color(2, 3, 4, 1.0)),
        ("hsl( 45, 25% , 25% )", Color(80, 72, 48)),
        ("hsla( 45, 25% , 25%, 0.35 )", Color(80, 72, 48, 0.35)),
    ],
)
def test_color_parse_input_has_spaces(input, output):
    assert Color.parse(input) == output


@pytest.mark.parametrize(
    "input,output",
    [
        ("rgb(300, 300, 300)", Color(255, 255, 255)),
        ("rgba(300, 300, 300, 300)", Color(255, 255, 255, 1.0)),
        ("hsl(400, 200%, 250%)", Color(255, 255, 255, 1.0)),
        ("hsla(400, 200%, 250%, 1.9)", Color(255, 255, 255, 1.0)),
    ],
)
def test_color_parse_clamp(input, output):
    assert Color.parse(input) == output


def test_color_parse_hsl_negative_degrees():
    assert Color.parse("hsl(-90, 50%, 50%)") == Color.parse("hsl(270, 50%, 50%)")


def test_color_parse_hsla_negative_degrees():
    assert Color.parse("hsla(-45, 50%, 50%, 0.2)") == Color.parse(
        "hsla(315, 50%, 50%, 0.2)"
    )


def test_color_parse_color():
    # as a convenience, if Color.parse is passed a color object, it will return it
    color = Color(20, 30, 40, 0.5)
    assert Color.parse(color) is color


@pytest.mark.parametrize(
    ["color1", "color2", "expected"],
    [
        # No alpha results in the RHS
        (Color(1, 2, 3), Color(20, 30, 40), Color(20, 30, 40)),
        # 0.9 alpha results in a blend 90% biased towards the RHS
        (Color(50, 100, 200), Color(10, 20, 30, 0.9), Color(14, 28, 47)),
        # Automatic color results in white or black
        (Color(200, 200, 200), Color.automatic(), Color(0, 0, 0)),
        (Color(20, 20, 20), Color.automatic(), Color(255, 255, 255)),
        # An automatic color will pick white or black and blend towards that
        (Color(200, 200, 200), Color.automatic(50), Color(100, 100, 100)),
        # Not a color produces NotImplemented
        (Color(1, 2, 3), "foo", NotImplemented),
    ],
)
def test_color_add(color1, color2, expected):
    assert color1.__add__(color2) == expected


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


def test_inverse():
    assert Color(55, 0, 255, 0.1).inverse == Color(200, 255, 0, 0.1)


def test_gradient_errors():
    with pytest.raises(ValueError):
        Gradient()
    with pytest.raises(ValueError):
        Gradient((0.1, Color.parse("red")))
    with pytest.raises(ValueError):
        Gradient((0.1, Color.parse("red")), (1, Color.parse("blue")))
    with pytest.raises(ValueError):
        Gradient((0, Color.parse("red")))

    with pytest.raises(ValueError):
        Gradient(
            (0, Color.parse("red")),
            (0.8, Color.parse("blue")),
        )

    with pytest.raises(ValueError):
        Gradient.from_colors(Color(200, 0, 0))


def test_gradient():
    gradient = Gradient(
        (0, Color(255, 0, 0)),
        (0.5, "blue"),
        (1, Color(0, 255, 0)),
        quality=11,
    )

    assert gradient.get_color(-1) == Color(255, 0, 0)
    assert gradient.get_color(0) == Color(255, 0, 0)
    assert gradient.get_color(1) == Color(0, 255, 0)
    assert gradient.get_color(1.2) == Color(0, 255, 0)
    assert gradient.get_color(0.5) == Color(0, 0, 255)
    assert gradient.get_color(0.7) == Color(0, 101, 153)


def test_is_transparent():
    """Check is_transparent is reporting correctly."""
    assert Color(0, 0, 0, 0).is_transparent
    assert Color(20, 20, 30, 0).is_transparent
    assert not Color(20, 20, 30, a=0.01).is_transparent
    assert not Color(20, 20, 30, a=1).is_transparent
    assert not Color(20, 20, 30, 0, ansi=1).is_transparent


@pytest.mark.parametrize(
    "base,tint,expected",
    [
        (
            Color(0, 0, 0),
            Color(10, 20, 30),
            Color(10, 20, 30),
        ),
        (
            Color(0, 0, 0, 0.5),
            Color(255, 255, 255, 0.5),
            Color(127, 127, 127, 0.5),
        ),
        (
            Color(100, 0, 0, 0.2),
            Color(0, 100, 0, 0.5),
            Color(50, 50, 0, 0.2),
        ),
        (Color(10, 20, 30), Color.parse("ansi_red"), Color(10, 20, 30)),
    ],
)
def test_tint(base: Color, tint: Color, expected: Color) -> None:
    assert base.tint(tint) == expected
