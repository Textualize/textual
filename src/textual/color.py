"""
This module contains a powerful Color class which Textual uses to expose colors.

The only exception would be for Rich renderables, which require a rich.color.Color instance.
You can convert from a Textual color to a Rich color with the [rich_color][textual.color.Color.rich_color] property.

## Named colors

The following named colors are used by the [parse][textual.color.Color.parse] method.

```{.rich columns="80" title="colors"}
from textual._color_constants import COLOR_NAME_TO_RGB
from textual.color import Color
from rich.table import Table
from rich.text import Text
table = Table("Name", "hex", "RGB", "Color", expand=True, highlight=True)

for name, triplet in sorted(COLOR_NAME_TO_RGB.items()):
    if len(triplet) != 3:
        continue
    color = Color(*triplet)
    r, g, b = triplet
    table.add_row(
        f'"{name}"',
        Text(f"{color.hex}", "bold green"),
        f"rgb({r}, {g}, {b})",
        Text("                    ", style=f"on rgb({r},{g},{b})")
    )
output = table
```


"""

from __future__ import annotations

import re
from colorsys import hls_to_rgb, rgb_to_hls
from functools import lru_cache
from operator import itemgetter
from typing import Callable, NamedTuple

import rich.repr
from rich.color import Color as RichColor
from rich.color import ColorType
from rich.color_triplet import ColorTriplet
from rich.style import Style
from rich.text import Text

from textual.css.scalar import percentage_string_to_float
from textual.css.tokenize import CLOSE_BRACE, COMMA, DECIMAL, OPEN_BRACE, PERCENT
from textual.suggestions import get_suggestion

from ._color_constants import COLOR_NAME_TO_RGB
from .geometry import clamp

_TRUECOLOR = ColorType.TRUECOLOR


class HSL(NamedTuple):
    """A color in HLS format."""

    h: float
    """Hue"""
    s: float
    """Saturation"""
    l: float
    """Lightness"""

    @property
    def css(self) -> str:
        """HSL in css format."""
        h, s, l = self

        def as_str(number: float) -> str:
            return f"{number:.1f}".rstrip("0").rstrip(".")

        return f"hsl({as_str(h*360)},{as_str(s*100)}%,{as_str(l*100)}%)"


class HSV(NamedTuple):
    """A color in HSV format."""

    h: float
    """Hue"""
    s: float
    """Saturation"""
    v: float
    """Value"""


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
_split_pairs3: Callable[[str], tuple[str, str, str]] = itemgetter(
    slice(0, 2), slice(2, 4), slice(4, 6)
)
# Fast way to split a string of 8 characters in to 4 pairs of 2 characters
_split_pairs4: Callable[[str], tuple[str, str, str, str]] = itemgetter(
    slice(0, 2), slice(2, 4), slice(4, 6), slice(6, 8)
)


class ColorParseError(Exception):
    """A color failed to parse.

    Args:
        message: The error message
        suggested_color: A close color we can suggest. Defaults to None.
    """

    def __init__(self, message: str, suggested_color: str | None = None):
        super().__init__(message)
        self.suggested_color = suggested_color


@rich.repr.auto
class Color(NamedTuple):
    """A class to represent a RGB color with an alpha component."""

    r: int
    """Red component (0-255)"""
    g: int
    """Green component (0-255)"""
    b: int
    """Blue component (0-255)"""
    a: float = 1.0
    """Alpha component (0-1)"""

    @classmethod
    def from_rich_color(cls, rich_color: RichColor) -> Color:
        """Create a new color from Rich's Color class.

        Args:
            rich_color: An instance of rich.color.Color.

        Returns:
            A new Color.
        """
        r, g, b = rich_color.get_truecolor()
        return cls(r, g, b)

    @classmethod
    def from_hsl(cls, h: float, s: float, l: float) -> Color:
        """Create a color from HLS components.

        Args:
            h: Hue.
            l: Lightness.
            s: Saturation.

        Returns:
            A new color.
        """
        r, g, b = hls_to_rgb(h, l, s)
        return cls(int(r * 255 + 0.5), int(g * 255 + 0.5), int(b * 255 + 0.5))

    def __rich__(self) -> Text:
        """A Rich method to show the color."""
        return Text(
            f" {self!r} ",
            style=Style.from_color(
                self.get_contrast_text().rich_color, self.rich_color
            ),
        )

    @property
    def inverse(self) -> Color:
        """The inverse of this color."""
        r, g, b, a = self
        return Color(255 - r, 255 - g, 255 - b, a)

    @property
    def is_transparent(self) -> bool:
        """Check if the color is transparent, i.e. has 0 alpha.

        Returns:
            True if transparent, otherwise False.

        """
        return self.a == 0

    @property
    def clamped(self) -> Color:
        """Get a color with all components saturated to maximum and minimum values.

        Returns:
            A color object.

        """
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
        """This color encoded in Rich's Color class.

        Returns:
            A color object as used by Rich.
        """
        r, g, b, _a = self
        return RichColor(
            f"#{r:02x}{g:02x}{b:02x}", _TRUECOLOR, None, ColorTriplet(r, g, b)
        )

    @property
    def normalized(self) -> tuple[float, float, float]:
        """A tuple of the color components normalized to between 0 and 1.

        Returns:
            Normalized components.

        """
        r, g, b, _a = self
        return (r / 255, g / 255, b / 255)

    @property
    def rgb(self) -> tuple[int, int, int]:
        """Get just the red, green, and blue components.

        Returns:
            Color components
        """
        r, g, b, _ = self
        return (r, g, b)

    @property
    def hsl(self) -> HSL:
        """Get the color as HSL.

        Returns:
            Color in HSL format.
        """
        r, g, b = self.normalized
        h, l, s = rgb_to_hls(r, g, b)
        return HSL(h, s, l)

    @property
    def brightness(self) -> float:
        """Get the human perceptual brightness.

        Returns:
            Brightness value (0-1).

        """
        r, g, b = self.normalized
        brightness = (299 * r + 587 * g + 114 * b) / 1000
        return brightness

    @property
    def hex(self) -> str:
        """The color in CSS hex form, with 6 digits for RGB, and 8 digits for RGBA.

        Returns:
            A CSS hex-style color, e.g. `"#46b3de"` or `"#3342457f"`

        """
        r, g, b, a = self.clamped
        return (
            f"#{r:02X}{g:02X}{b:02X}"
            if a == 1
            else f"#{r:02X}{g:02X}{b:02X}{int(a*255):02X}"
        )

    @property
    def hex6(self) -> str:
        """The color in CSS hex form, with 6 digits for RGB. Alpha is ignored.

        Returns:
            A CSS hex-style color, e.g. "#46b3de"

        """
        r, g, b, a = self.clamped
        return f"#{r:02X}{g:02X}{b:02X}"

    @property
    def css(self) -> str:
        """The color in CSS rgb or rgba form.

        Returns:
            A CSS style color, e.g. `"rgb(10,20,30)"` or `"rgb(50,70,80,0.5)"`

        """
        r, g, b, a = self
        return f"rgb({r},{g},{b})" if a == 1 else f"rgba({r},{g},{b},{a})"

    @property
    def monochrome(self) -> Color:
        """Get a monochrome version of this color.

        Returns:
            A new monochrome color.
        """
        r, g, b, a = self
        gray = round(r * 0.2126 + g * 0.7152 + b * 0.0722)
        return Color(gray, gray, gray, a)

    def __rich_repr__(self) -> rich.repr.Result:
        r, g, b, a = self
        yield r
        yield g
        yield b
        yield "a", a

    def with_alpha(self, alpha: float) -> Color:
        """Create a new color with the given alpha.

        Args:
            alpha: New value for alpha.

        Returns:
            A new color.
        """
        r, g, b, _ = self
        return Color(r, g, b, alpha)

    def blend(
        self, destination: Color, factor: float, alpha: float | None = None
    ) -> Color:
        """Generate a new color between two colors.

        Args:
            destination: Another color.
            factor: A blend factor, 0 -> 1.
            alpha: New alpha for result. Defaults to None.

        Returns:
            A new color.
        """
        if factor == 0:
            return self
        elif factor == 1:
            return destination
        r1, g1, b1, a1 = self
        r2, g2, b2, a2 = destination

        if alpha is None:
            new_alpha = a1 + (a2 - a1) * factor
        else:
            new_alpha = alpha

        return Color(
            int(r1 + (r2 - r1) * factor),
            int(g1 + (g2 - g1) * factor),
            int(b1 + (b2 - b1) * factor),
            new_alpha,
        )

    def __add__(self, other: object) -> Color:
        if isinstance(other, Color):
            new_color = self.blend(other, other.a, alpha=1.0)
            return new_color
        return NotImplemented

    @classmethod
    @lru_cache(maxsize=1024 * 4)
    def parse(cls, color_text: str | Color) -> Color:
        """Parse a string containing a named color or CSS-style color.

        Colors may be parsed from the following formats:

        - Text beginning with a `#` is parsed as a hexadecimal color code,
         where R, G, B, and A must be hexadecimal digits (0-9A-F):

            - `#RGB`
            - `#RGBA`
            - `#RRGGBB`
            - `#RRGGBBAA`

        - Alternatively, RGB colors can also be specified in the format
         that follows, where R, G, and B must be numbers between 0 and 255
         and A must be a value between 0 and 1:

            - `rgb(R,G,B)`
            - `rgb(R,G,B,A)`

        - The HSL model can also be used, with a syntax similar to the above,
         if H is a value between 0 and 360, S and L are percentages, and A
         is a value between 0 and 1:

            - `hsl(H,S,L)`
            - `hsla(H,S,L,A)`

        Any other formats will raise a `ColorParseError`.

        Args:
            color_text: Text with a valid color format. Color objects will
                be returned unmodified.

        Raises:
            ColorParseError: If the color is not encoded correctly.

        Returns:
            Instance encoding the color specified by the argument.
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
                suggested_color = get_suggestion(
                    color_text, list(COLOR_NAME_TO_RGB.keys())
                )
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
            r, g, b = rgb_hex_triple  # type: ignore[misc]
            color = cls(int(f"{r}{r}", 16), int(f"{g}{g}", 16), int(f"{b}{b}", 16))
        elif rgb_hex_quad is not None:
            r, g, b, a = rgb_hex_quad  # type: ignore[misc]
            color = cls(
                int(f"{r}{r}", 16),
                int(f"{g}{g}", 16),
                int(f"{b}{b}", 16),
                int(f"{a}{a}", 16) / 255.0,
            )
        elif rgb_hex is not None:
            r, g, b = [int(pair, 16) for pair in _split_pairs3(rgb_hex)]
            color = cls(r, g, b, 1.0)
        elif rgba_hex is not None:
            r, g, b, a = [int(pair, 16) for pair in _split_pairs4(rgba_hex)]
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
            color = Color.from_hsl(h, s, l)
        elif hsla is not None:
            h, s, l, a = hsla.split(",")
            h = float(h) % 360 / 360
            s = percentage_string_to_float(s)
            l = percentage_string_to_float(l)
            a = clamp(float(a), 0.0, 1.0)
            color = Color.from_hsl(h, s, l).with_alpha(a)
        else:
            raise AssertionError("Can't get here if RE_COLOR matches")
        return color

    @lru_cache(maxsize=1024)
    def darken(self, amount: float, alpha: float | None = None) -> Color:
        """Darken the color by a given amount.

        Args:
            amount: Value between 0-1 to reduce luminance by.
            alpha: Alpha component for new color or None to copy alpha. Defaults to None.

        Returns:
            New color.
        """
        l, a, b = rgb_to_lab(self)
        l -= amount * 100
        return lab_to_rgb(Lab(l, a, b), self.a if alpha is None else alpha).clamped

    def lighten(self, amount: float, alpha: float | None = None) -> Color:
        """Lighten the color by a given amount.

        Args:
            amount: Value between 0-1 to increase luminance by.
            alpha: Alpha component for new color or None to copy alpha. Defaults to None.

        Returns:
            New color.
        """
        return self.darken(-amount, alpha)

    @lru_cache(maxsize=1024)
    def get_contrast_text(self, alpha=0.95) -> Color:
        """Get a light or dark color that best contrasts this color, for use with text.

        Args:
            alpha: An alpha value to adjust the pure white / black by.
                Defaults to 0.95.

        Returns:
            A new color, either an off-white or off-black
        """
        brightness = self.brightness
        white_contrast = abs(brightness - WHITE.brightness)
        black_contrast = abs(brightness - BLACK.brightness)
        return (WHITE if white_contrast > black_contrast else BLACK).with_alpha(alpha)


# Color constants
WHITE = Color(255, 255, 255)
BLACK = Color(0, 0, 0)


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


def lab_to_rgb(lab: Lab, alpha: float = 1.0) -> Color:
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

    return Color(int(r * 255), int(g * 255), int(b * 255), alpha)
