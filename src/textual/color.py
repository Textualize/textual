from __future__ import annotations

from colorsys import rgb_to_hls, rgb_to_hsv, hls_to_rgb, hsv_to_rgb
from functools import lru_cache
import re
from operator import itemgetter
from typing import Callable, NamedTuple

import rich.repr
from rich.color import Color as RichColor
from rich.style import Style
from rich.text import Text


from . import log
from ._color_constants import ANSI_COLOR_TO_RGB
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


RE_COLOR = re.compile(
    r"""^
\#([0-9a-fA-F]{6})$|
\#([0-9a-fA-F]{8})$|
rgb\((\-?\d+\.?\d*,\-?\d+\.?\d*,\-?\d+\.?\d*)\)$|
rgba\((\-?\d+\.?\d*,\-?\d+\.?\d*,\-?\d+\.?\d*,\-?\d+\.?\d*)\)$
""",
    re.VERBOSE,
)

# Fast way to split a string of 8 characters in to 3 pairs of 2 characters
split_pairs3: Callable[[str], tuple[str, str, str]] = itemgetter(
    slice(0, 2), slice(2, 4), slice(4, 6)
)
# Fast way to split a string of 8 characters in to 4 pairs of 2 characters
split_pairs4: Callable[[str], tuple[str, str, str, str]] = itemgetter(
    slice(0, 2), slice(2, 4), slice(4, 6), slice(6, 8)
)


class ColorParseError(Exception):
    """A color failed to parse"""


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
        return cls(int(r * 255), int(g * 255), int(b * 255))

    @classmethod
    def from_hsv(cls, h: float, s: float, v: float) -> Color:
        """Create a color from HSV components.

        Args:
            h (float): Hue
            s (float): Saturation
            v (float): Value

        Returns:
            Color: A new Color.
        """
        r, g, b = hsv_to_rgb(h, s, v)
        return cls(int(r * 255), int(g * 255), int(b * 255))

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
        r, g, b, _a = self
        return RichColor.from_rgb(r, g, b)

    @property
    def normalized(self) -> tuple[float, float, float]:
        """A tuple of the color components normalized to between 0 and 1."""
        r, g, b, _a = self
        return (r / 255, g / 255, b / 255)

    @property
    def hls(self) -> HLS:
        """Get the color as HLS."""
        r, g, b = self.normalized
        return HLS(*rgb_to_hls(r, g, b))

    @property
    def hsv(self) -> HSV:
        """Get the color as HSV."""
        r, g, b = self.normalized
        return HSV(*rgb_to_hsv(r, g, b))

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

    @lru_cache(maxsize=2048)
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
    def parse(cls, color_text: str) -> Color:
        """Parse a string containing a CSS-style color.

        Args:
            color_text (str): Text with a valid color format.

        Raises:
            ColorParseError: If the color is not encoded correctly.

        Returns:
            Color: New color object.
        """

        ansi_color = ANSI_COLOR_TO_RGB.get(color_text)
        if ansi_color is not None:
            return cls(*ansi_color)
        color_match = RE_COLOR.match(color_text)
        if color_match is None:
            raise ColorParseError(f"failed to parse {color_text!r} as a color")
        rgb_hex, rgba_hex, rgb, rgba = color_match.groups()

        if rgb_hex is not None:
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
        else:
            raise AssertionError("Can't get here if RE_COLOR matches")
        return color

    def darken(self, amount: float) -> Color:
        """Darken the color by a given amount.

        Args:
            amount (float): Value between 0-1 to reduce luminance by.

        Returns:
            Color: New color.
        """
        h, l, s = self.hls
        color = self.from_hls(h, l - amount, s)
        return color.clamped

    def lighten(self, amount: float) -> Color:
        """Lighten the color by a given amount.

        Args:
            amount (float): Value between 0-1 to increase luminance by.

        Returns:
            Color: New color.
        """
        return self.darken(-amount).clamped

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
