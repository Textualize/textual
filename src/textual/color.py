"""
Manages Color in Textual.

All instances where the developer is presented with a color should use this class. The only
exception should be when passing things to a Rich renderable, which will need to use the
`rich_color` attribute to perform a conversion.

I'm not entirely happy with burdening the user with two similar color classes. In a future
update we might add a protocol to convert automatically so the dev could use them interchangably.

"""

from __future__ import annotations

from colorsys import rgb_to_hls, hls_to_rgb
from functools import lru_cache
import re
from operator import itemgetter
from typing import Callable, NamedTuple

import rich.repr
from rich.color import Color as RichColor
from rich.style import Style
from rich.text import Text

from textual.css.scalar import percentage_string_to_float
from textual.css.tokenize import COMMA, OPEN_BRACE, CLOSE_BRACE, DECIMAL, PERCENT
from textual.suggestions import get_suggestion
from ._color_constants import COLOR_NAME_TO_RGB
from .geometry import clamp


class HLS(NamedTuple):
    """A color in HLS format."""

    h: float
    l: float
    s: float


class HSV(NamedTuple):
    """A color in HSV format."""

    h: float
    s: float
    v: float


class Lab(NamedTuple):
    """A color in CIE-L*ab format."""

    L: float
    a: float
    b: float


RE_COLOR = re.compile(
    rf"""^
\#([0-9a-fA-F]{{3}})$|
\#([0-9a-fA-F]{{4}})$|
\#([0-9a-fA-F]{{6}})$|
\#([0-9a-fA-F]{{8}})$|
rgb{OPEN_BRACE}({DECIMAL}{COMMA}{DECIMAL}{COMMA}{DECIMAL}){CLOSE_BRACE}$|
rgba{OPEN_BRACE}({DECIMAL}{COMMA}{DECIMAL}{COMMA}{DECIMAL}{COMMA}{DECIMAL}){CLOSE_BRACE}$|
hsl{OPEN_BRACE}({DECIMAL}{COMMA}{PERCENT}{COMMA}{PERCENT}){CLOSE_BRACE}$|
hsla{OPEN_BRACE}({DECIMAL}{COMMA}{PERCENT}{COMMA}{PERCENT}{COMMA}{DECIMAL}){CLOSE_BRACE}$
""",
    re.VERBOSE,
)

# Fast way to split a string of 6 characters in to 3 pairs of 2 characters
split_pairs3: Callable[[str], tuple[str, str, str]] = itemgetter(
    slice(0, 2), slice(2, 4), slice(4, 6)
)
# Fast way to split a string of 8 characters in to 4 pairs of 2 characters
split_pairs4: Callable[[str], tuple[str, str, str, str]] = itemgetter(
    slice(0, 2), slice(2, 4), slice(4, 6), slice(6, 8)
)


class ColorParseError(Exception):
    """A color failed to parse"""

    def __init__(self, message: str, suggested_color: str | None = None):
        """
        Creates a new ColorParseError

        Args:
            message (str): the error message
            suggested_color (str | None): a close color we can suggest. Defaults to None.
        """
        super().__init__(message)
        self.suggested_color = suggested_color


@rich.repr.auto
class Color(NamedTuple):
    """A class to represent a single RGB color with alpha."""

    r: int
    g: int
    b: int
    a: float = 1.0

    @classmethod
    def from_rich_color(cls, rich_color: RichColor) -> Color:
        """Create a new color from Rich's Color class.

        Args:
            rich_color (RichColor): An instance of rich.color.Color.

        Returns:
            Color: A new Color.
        """
        r, g, b = rich_color.get_truecolor()
        return cls(r, g, b)

    @classmethod
    def from_hls(cls, h: float, l: float, s: float) -> Color:
        """Create a color from HLS components.

        Args:
            h (float): Hue.
            l (float): Lightness.
            s (float): Saturation.

        Returns:
            Color: A new color.
        """
        r, g, b = hls_to_rgb(h, l, s)
        return cls(int(r * 255 + 0.5), int(g * 255 + 0.5), int(b * 255 + 0.5))

    def __rich__(self) -> Text:
        """A Rich method to show the color."""
        r, g, b, _ = self
        return Text(
            f" {self!r} ",
            style=Style.from_color(
                self.get_contrast_text().rich_color, RichColor.from_rgb(r, g, b)
            ),
        )

    @property
    def is_transparent(self) -> bool:
        """Check if the color is transparent, i.e. has 0 alpha."""
        return self.a == 0

    @property
    def clamped(self) -> Color:
        """Get a color with all components saturated to maximum and minimum values."""
        r, g, b, a = self
        _clamp = clamp
        color = Color(
            _clamp(r, 0, 255),
            _clamp(g, 0, 255),
            _clamp(b, 0, 255),
            _clamp(a, 0.0, 1.0),
        )
        return color

    @property
    def rich_color(self) -> RichColor:
        """This color encoded in Rich's Color class."""
        # TODO: This isn't cheap as I'd like - cache in a LRUCache ?
        r, g, b, _a = self
        return RichColor.from_rgb(r, g, b)

    @property
    def normalized(self) -> tuple[float, float, float]:
        """A tuple of the color components normalized to between 0 and 1."""
        r, g, b, _a = self
        return (r / 255, g / 255, b / 255)

    @property
    def rgb(self) -> tuple[int, int, int]:
        """Get just the red, green, and blue components."""
        r, g, b, _ = self
        return (r, g, b)

    @property
    def hls(self) -> HLS:
        """Get the color as HLS."""
        r, g, b = self.normalized
        return HLS(*rgb_to_hls(r, g, b))

    @property
    def brightness(self) -> float:
        """Get the human perceptual brightness."""
        r, g, b = self.normalized
        brightness = (299 * r + 587 * g + 114 * b) / 1000
        return brightness

    @property
    def hex(self) -> str:
        """The color in CSS hex form, with 6 digits for RGB, and 8 digits for RGBA.

        Returns:
            str: A CSS hex-style color, e.g. "#46b3de" or "#3342457f"

        """
        r, g, b, a = self
        return (
            f"#{r:02X}{g:02X}{b:02X}"
            if a == 1
            else f"#{r:02X}{g:02X}{b:02X}{int(a*255):02X}"
        )

    @property
    def css(self) -> str:
        """The color in CSS rgb or rgba form.

        Returns:
            str: A CSS style color, e.g. "rgb(10,20,30)" or "rgb(50,70,80,0.5)"

        """
        r, g, b, a = self
        return f"rgb({r},{g},{b})" if a == 1 else f"rgba({r},{g},{b},{a})"

    def __rich_repr__(self) -> rich.repr.Result:
        r, g, b, a = self
        yield r
        yield g
        yield b
        yield "a", a

    def with_alpha(self, alpha: float) -> Color:
        """Create a new color with the given alpha.

        Args:
            alpha (float): New value for alpha.

        Returns:
            Color: A new color.
        """
        r, g, b, _ = self
        return Color(r, g, b, alpha)

    def blend(self, destination: Color, factor: float) -> Color:
        """Generate a new color between two colors.

        Args:
            destination (Color): Another color.
            factor (float): A blend factor, 0 -> 1

        Returns:
            Color: A new color.
        """
        if factor == 0:
            return self
        elif factor == 1:
            return destination
        r1, g1, b1, _ = self
        r2, g2, b2, _ = destination
        return Color(
            int(r1 + (r2 - r1) * factor),
            int(g1 + (g2 - g1) * factor),
            int(b1 + (b2 - b1) * factor),
        )

    def __add__(self, other: object) -> Color:
        if isinstance(other, Color):
            new_color = self.blend(other, other.a)
            return new_color
        return NotImplemented

    @classmethod
    @lru_cache(maxsize=1024 * 4)
    def parse(cls, color_text: str | Color) -> Color:
        """Parse a string containing a CSS-style color.

        Args:
            color_text (str | Color): Text with a valid color format. Color objects will
                be returned unmodified.

        Raises:
            ColorParseError: If the color is not encoded correctly.

        Returns:
            Color: New color object.
        """
        if isinstance(color_text, Color):
            return color_text
        color_from_name = COLOR_NAME_TO_RGB.get(color_text)
        if color_from_name is not None:
            return cls(*color_from_name)
        color_match = RE_COLOR.match(color_text)
        if color_match is None:
            error_message = f"failed to parse {color_text!r} as a color"
            suggested_color = None
            if not color_text.startswith(("#", "rgb", "hsl")):
                # Seems like we tried to use a color name: let's try to find one that is close enough:
                suggested_color = get_suggestion(color_text, COLOR_NAME_TO_RGB.keys())
                if suggested_color:
                    error_message += f"; did you mean '{suggested_color}'?"
            raise ColorParseError(error_message, suggested_color)
        (
            rgb_hex_triple,
            rgb_hex_quad,
            rgb_hex,
            rgba_hex,
            rgb,
            rgba,
            hsl,
            hsla,
        ) = color_match.groups()

        if rgb_hex_triple is not None:
            r, g, b = rgb_hex_triple
            color = cls(int(f"{r}{r}", 16), int(f"{g}{g}", 16), int(f"{b}{b}", 16))
        elif rgb_hex_quad is not None:
            r, g, b, a = rgb_hex_quad
            color = cls(
                int(f"{r}{r}", 16),
                int(f"{g}{g}", 16),
                int(f"{b}{b}", 16),
                int(f"{a}{a}", 16) / 255.0,
            )
        elif rgb_hex is not None:
            r, g, b = [int(pair, 16) for pair in split_pairs3(rgb_hex)]
            color = cls(r, g, b, 1.0)
        elif rgba_hex is not None:
            r, g, b, a = [int(pair, 16) for pair in split_pairs4(rgba_hex)]
            color = cls(r, g, b, a / 255.0)
        elif rgb is not None:
            r, g, b = [clamp(int(float(value)), 0, 255) for value in rgb.split(",")]
            color = cls(r, g, b, 1.0)
        elif rgba is not None:
            float_r, float_g, float_b, float_a = [
                float(value) for value in rgba.split(",")
            ]
            color = cls(
                clamp(int(float_r), 0, 255),
                clamp(int(float_g), 0, 255),
                clamp(int(float_b), 0, 255),
                clamp(float_a, 0.0, 1.0),
            )
        elif hsl is not None:
            h, s, l = hsl.split(",")
            h = float(h) % 360 / 360
            s = percentage_string_to_float(s)
            l = percentage_string_to_float(l)
            color = Color.from_hls(h, l, s)
        elif hsla is not None:
            h, s, l, a = hsla.split(",")
            h = float(h) % 360 / 360
            s = percentage_string_to_float(s)
            l = percentage_string_to_float(l)
            a = clamp(float(a), 0.0, 1.0)
            color = Color.from_hls(h, l, s).with_alpha(a)
        else:
            raise AssertionError("Can't get here if RE_COLOR matches")
        return color

    @lru_cache(maxsize=1024)
    def darken(self, amount: float) -> Color:
        """Darken the color by a given amount.

        Args:
            amount (float): Value between 0-1 to reduce luminance by.

        Returns:
            Color: New color.
        """
        l, a, b = rgb_to_lab(self)
        l -= amount * 100
        return lab_to_rgb(Lab(l, a, b)).clamped

    def lighten(self, amount: float) -> Color:
        """Lighten the color by a given amount.

        Args:
            amount (float): Value between 0-1 to increase luminance by.

        Returns:
            Color: New color.
        """
        return self.darken(-amount).clamped

    @lru_cache(maxsize=1024)
    def get_contrast_text(self, alpha=0.95) -> Color:
        """Get a light or dark color that best contrasts this color, for use with text.

        Args:
            alpha (float, optional): An alpha value to adjust the pure white / black by.
                Defaults to 0.95.

        Returns:
            Color: A new color, either an off-white or off-black
        """
        white = self.blend(WHITE, alpha)
        black = self.blend(BLACK, alpha)
        brightness = self.brightness
        white_contrast = abs(brightness - white.brightness)
        black_contrast = abs(brightness - black.brightness)
        return white if white_contrast > black_contrast else black


# Color constants
WHITE = Color(255, 255, 255)
BLACK = Color(0, 0, 0)
TRANSPARENT = Color(0, 0, 0, 0)


class ColorPair(NamedTuple):
    """A pair of colors for foreground and background."""

    foreground: Color
    background: Color

    def __rich_repr__(self) -> rich.repr.Result:
        yield "foreground", self.foreground
        yield "background", self.background

    @property
    def style(self) -> Style:
        """A Rich style with foreground and background."""
        return self._get_style()

    @lru_cache(maxsize=1024 * 4)
    def _get_style(self) -> Style:
        """Get a Rich style, foreground adjusted for transparency."""
        r, g, b, a = self.foreground
        if a == 0:
            return Style.from_color(
                self.background.rich_color, self.background.rich_color
            )
        elif a == 1:
            return Style.from_color(
                self.foreground.rich_color, self.background.rich_color
            )
        else:
            r2, g2, b2, _ = self.background
            return Style.from_color(
                RichColor.from_rgb(
                    r + (r2 - r) * a, g + (g2 - g) * a, b + (b2 - b) * a
                ),
                self.background.rich_color,
            )


def rgb_to_lab(rgb: Color) -> Lab:
    """Convert an RGB color to the CIE-L*ab format.

    Uses the standard RGB color space with a D65/2⁰ standard illuminant.
    Conversion passes through the XYZ color space.
    Cf. http://www.easyrgb.com/en/math.php.
    """

    r, g, b = rgb.r / 255, rgb.g / 255, rgb.b / 255

    r = pow((r + 0.055) / 1.055, 2.4) if r > 0.04045 else r / 12.92
    g = pow((g + 0.055) / 1.055, 2.4) if g > 0.04045 else g / 12.92
    b = pow((b + 0.055) / 1.055, 2.4) if b > 0.04045 else b / 12.92

    x = (r * 41.24 + g * 35.76 + b * 18.05) / 95.047
    y = (r * 21.26 + g * 71.52 + b * 7.22) / 100
    z = (r * 1.93 + g * 11.92 + b * 95.05) / 108.883

    off = 16 / 116
    x = pow(x, 1 / 3) if x > 0.008856 else 7.787 * x + off
    y = pow(y, 1 / 3) if y > 0.008856 else 7.787 * y + off
    z = pow(z, 1 / 3) if z > 0.008856 else 7.787 * z + off

    return Lab(116 * y - 16, 500 * (x - y), 200 * (y - z))


def lab_to_rgb(lab: Lab) -> Color:
    """Convert a CIE-L*ab color to RGB.

    Uses the standard RGB color space with a D65/2⁰ standard illuminant.
    Conversion passes through the XYZ color space.
    Cf. http://www.easyrgb.com/en/math.php.
    """

    y = (lab.L + 16) / 116
    x = lab.a / 500 + y
    z = y - lab.b / 200

    off = 16 / 116
    y = pow(y, 3) if y > 0.2068930344 else (y - off) / 7.787
    x = 0.95047 * pow(x, 3) if x > 0.2068930344 else 0.122059 * (x - off)
    z = 1.08883 * pow(z, 3) if z > 0.2068930344 else 0.139827 * (z - off)

    r = x * 3.2406 + y * -1.5372 + z * -0.4986
    g = x * -0.9689 + y * 1.8758 + z * 0.0415
    b = x * 0.0557 + y * -0.2040 + z * 1.0570

    r = 1.055 * pow(r, 1 / 2.4) - 0.055 if r > 0.0031308 else 12.92 * r
    g = 1.055 * pow(g, 1 / 2.4) - 0.055 if g > 0.0031308 else 12.92 * g
    b = 1.055 * pow(b, 1 / 2.4) - 0.055 if b > 0.0031308 else 12.92 * b

    return Color(int(r * 255), int(g * 255), int(b * 255))


if __name__ == "__main__":

    from rich import print

    c1 = Color.parse("#112233")
    print(c1, c1.hex, c1.css)

    c2 = Color.parse("#11223344")
    print(c2)

    c3 = Color.parse("rgb(10,20,30)")
    print(c3)

    c4 = Color.parse("rgba(10,20,30,0.5)")
    print(c4, c4.hex, c4.css)

    p1 = ColorPair(c4, c1)
    print(p1)

    print(p1.style)

    print(Color.parse("dark_blue"))
