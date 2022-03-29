from __future__ import annotations

import re
from typing import NamedTuple

from .geometry import clamp
import rich.repr
from rich.color import Color as RichColor
from rich.style import Style

ANSI_COLOR_NAMES = {
    "black": 0,
    "red": 1,
    "green": 2,
    "yellow": 3,
    "blue": 4,
    "magenta": 5,
    "cyan": 6,
    "white": 7,
    "bright_black": 8,
    "bright_red": 9,
    "bright_green": 10,
    "bright_yellow": 11,
    "bright_blue": 12,
    "bright_magenta": 13,
    "bright_cyan": 14,
    "bright_white": 15,
    "grey0": 16,
    "gray0": 16,
    "navy_blue": 17,
    "dark_blue": 18,
    "blue3": 20,
    "blue1": 21,
    "dark_green": 22,
    "deep_sky_blue4": 25,
    "dodger_blue3": 26,
    "dodger_blue2": 27,
    "green4": 28,
    "spring_green4": 29,
    "turquoise4": 30,
    "deep_sky_blue3": 32,
    "dodger_blue1": 33,
    "green3": 40,
    "spring_green3": 41,
    "dark_cyan": 36,
    "light_sea_green": 37,
    "deep_sky_blue2": 38,
    "deep_sky_blue1": 39,
    "spring_green2": 47,
    "cyan3": 43,
    "dark_turquoise": 44,
    "turquoise2": 45,
    "green1": 46,
    "spring_green1": 48,
    "medium_spring_green": 49,
    "cyan2": 50,
    "cyan1": 51,
    "dark_red": 88,
    "deep_pink4": 125,
    "purple4": 55,
    "purple3": 56,
    "blue_violet": 57,
    "orange4": 94,
    "grey37": 59,
    "gray37": 59,
    "medium_purple4": 60,
    "slate_blue3": 62,
    "royal_blue1": 63,
    "chartreuse4": 64,
    "dark_sea_green4": 71,
    "pale_turquoise4": 66,
    "steel_blue": 67,
    "steel_blue3": 68,
    "cornflower_blue": 69,
    "chartreuse3": 76,
    "cadet_blue": 73,
    "sky_blue3": 74,
    "steel_blue1": 81,
    "pale_green3": 114,
    "sea_green3": 78,
    "aquamarine3": 79,
    "medium_turquoise": 80,
    "chartreuse2": 112,
    "sea_green2": 83,
    "sea_green1": 85,
    "aquamarine1": 122,
    "dark_slate_gray2": 87,
    "dark_magenta": 91,
    "dark_violet": 128,
    "purple": 129,
    "light_pink4": 95,
    "plum4": 96,
    "medium_purple3": 98,
    "slate_blue1": 99,
    "yellow4": 106,
    "wheat4": 101,
    "grey53": 102,
    "gray53": 102,
    "light_slate_grey": 103,
    "light_slate_gray": 103,
    "medium_purple": 104,
    "light_slate_blue": 105,
    "dark_olive_green3": 149,
    "dark_sea_green": 108,
    "light_sky_blue3": 110,
    "sky_blue2": 111,
    "dark_sea_green3": 150,
    "dark_slate_gray3": 116,
    "sky_blue1": 117,
    "chartreuse1": 118,
    "light_green": 120,
    "pale_green1": 156,
    "dark_slate_gray1": 123,
    "red3": 160,
    "medium_violet_red": 126,
    "magenta3": 164,
    "dark_orange3": 166,
    "indian_red": 167,
    "hot_pink3": 168,
    "medium_orchid3": 133,
    "medium_orchid": 134,
    "medium_purple2": 140,
    "dark_goldenrod": 136,
    "light_salmon3": 173,
    "rosy_brown": 138,
    "grey63": 139,
    "gray63": 139,
    "medium_purple1": 141,
    "gold3": 178,
    "dark_khaki": 143,
    "navajo_white3": 144,
    "grey69": 145,
    "gray69": 145,
    "light_steel_blue3": 146,
    "light_steel_blue": 147,
    "yellow3": 184,
    "dark_sea_green2": 157,
    "light_cyan3": 152,
    "light_sky_blue1": 153,
    "green_yellow": 154,
    "dark_olive_green2": 155,
    "dark_sea_green1": 193,
    "pale_turquoise1": 159,
    "deep_pink3": 162,
    "magenta2": 200,
    "hot_pink2": 169,
    "orchid": 170,
    "medium_orchid1": 207,
    "orange3": 172,
    "light_pink3": 174,
    "pink3": 175,
    "plum3": 176,
    "violet": 177,
    "light_goldenrod3": 179,
    "tan": 180,
    "misty_rose3": 181,
    "thistle3": 182,
    "plum2": 183,
    "khaki3": 185,
    "light_goldenrod2": 222,
    "light_yellow3": 187,
    "grey84": 188,
    "gray84": 188,
    "light_steel_blue1": 189,
    "yellow2": 190,
    "dark_olive_green1": 192,
    "honeydew2": 194,
    "light_cyan1": 195,
    "red1": 196,
    "deep_pink2": 197,
    "deep_pink1": 199,
    "magenta1": 201,
    "orange_red1": 202,
    "indian_red1": 204,
    "hot_pink": 206,
    "dark_orange": 208,
    "salmon1": 209,
    "light_coral": 210,
    "pale_violet_red1": 211,
    "orchid2": 212,
    "orchid1": 213,
    "orange1": 214,
    "sandy_brown": 215,
    "light_salmon1": 216,
    "light_pink1": 217,
    "pink1": 218,
    "plum1": 219,
    "gold1": 220,
    "navajo_white1": 223,
    "misty_rose1": 224,
    "thistle1": 225,
    "yellow1": 226,
    "light_goldenrod1": 227,
    "khaki1": 228,
    "wheat1": 229,
    "cornsilk1": 230,
    "grey100": 231,
    "gray100": 231,
    "grey3": 232,
    "gray3": 232,
    "grey7": 233,
    "gray7": 233,
    "grey11": 234,
    "gray11": 234,
    "grey15": 235,
    "gray15": 235,
    "grey19": 236,
    "gray19": 236,
    "grey23": 237,
    "gray23": 237,
    "grey27": 238,
    "gray27": 238,
    "grey30": 239,
    "gray30": 239,
    "grey35": 240,
    "gray35": 240,
    "grey39": 241,
    "gray39": 241,
    "grey42": 242,
    "gray42": 242,
    "grey46": 243,
    "gray46": 243,
    "grey50": 244,
    "gray50": 244,
    "grey54": 245,
    "gray54": 245,
    "grey58": 246,
    "gray58": 246,
    "grey62": 247,
    "gray62": 247,
    "grey66": 248,
    "gray66": 248,
    "grey70": 249,
    "gray70": 249,
    "grey74": 250,
    "gray74": 250,
    "grey78": 251,
    "gray78": 251,
    "grey82": 252,
    "gray82": 252,
    "grey85": 253,
    "gray85": 253,
    "grey89": 254,
    "gray89": 254,
    "grey93": 255,
    "gray93": 255,
}


RE_COLOR = re.compile(
    r"""^
\#([0-9a-fA-F]{6})$|
\#([0-9a-fA-F]{8})$|
rgb\((\-?\d+\.?\d*,\-?\d+\.?\d*,\-?\d+\.?\d*)\)$|
rgba\((\-?\d+\.?\d*,\-?\d+\.?\d*,\-?\d+\.?\d*,\-?\d+\.?\d*)\)$
""",
    re.VERBOSE,
)


class ColorParseError(Exception):
    """A color failed to parse"""


@rich.repr.auto
class Color(NamedTuple):
    r: int
    g: int
    b: int
    a: float

    @property
    def rich_color(self) -> RichColor:
        r, g, b, _a = self
        return RichColor.from_rgb(r, g, b)

    @property
    def hex(self) -> str:
        r, g, b, a = self
        return (
            f"#{r:02X}{g:02X}{b:02X}"
            if a == 1
            else f"#{r:02X}{g:02X}{b:02X}{int(a*255):02X}"
        )

    @property
    def css(self) -> str:
        r, g, b, a = self
        return f"rgb({r},{g},{b})" if a == 1 else f"rgba({r},{g},{b},{a})"

    def __rich_repr__(self) -> rich.repr.Result:
        r, g, b, a = self
        yield r
        yield g
        yield b
        yield "a", a

    @classmethod
    def parse(cls, color_text: str) -> Color:
        color_match = RE_COLOR.match(color_text)
        if color_match is None:
            raise ColorParseError(f"failed to parse {color_text!r} as a color")
        rgb_hex, rgba_hex, rgb, rgba = color_match.groups()

        if rgb_hex is not None:
            color = cls(
                int(rgb_hex[0:2], 16), int(rgb_hex[2:4], 16), int(rgb_hex[4:6], 16), 1
            )
        elif rgba_hex is not None:
            color = cls(
                int(rgba_hex[0:2], 16),
                int(rgba_hex[2:4], 16),
                int(rgba_hex[4:6], 16),
                float(int(rgba_hex[6:8], 16)) / 255.0,
            )
        elif rgb is not None:
            r, g, b = [clamp(float(value), 0, 255) for value in rgb.split(",")]
            color = cls(int(r), int(g), int(b), 1.0)
        elif rgba is not None:
            r, g, b, a = [float(value) for value in rgba.split(",")]
            color = Color(
                clamp(int(r), 0, 255),
                clamp(int(g), 0, 255),
                clamp(int(b), 0, 255),
                clamp(a, 0.0, 1.0),
            )
        else:
            raise AssertionError("Can't get here if RE_COLOR matches")
        return color


class ColorPair(NamedTuple):
    foreground: Color
    background: Color

    def __rich_repr__(self) -> rich.repr.Result:
        yield "foreground", self.foreground
        yield "background", self.background

    @property
    def style(self) -> Style:
        """A Rich style with foreground and background"""
        r, g, b, a = self.foreground
        if a == 0:
            return Style(
                color=self.background.rich_color, bgcolor=self.background.rich_color
            )
        elif a == 1:
            return Style(
                color=self.foreground.rich_color, bgcolor=self.background.rich_color
            )
        else:
            r2, g2, b2, _ = self.background
            return Style(
                color=RichColor.from_rgb(
                    r + (r2 - r) * a, g + (g2 - g) * a, b + (b2 - b) * a
                ),
                bgcolor=self.background.rich_color,
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
