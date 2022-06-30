"""
Helper functions to work with Textual Colors.
"""

from __future__ import annotations
import re

from textual.color import Color
from textual.css.scalar import Scalar
from textual.css.tokenize import DECIMAL


RE_ALPHA = (
    # Color expressions themselves can contain percentage values (e.g. `hsl( 180, 50%, 50% )`), so we'll only
    # consider a percentage expression to be an alpha value if it's at the start or the end of the color expression.
    # (i.e. `color: red 50%` or `color: 50% red`)
    re.compile(rf"^({DECIMAL})%"),  # starting with a percentage
    re.compile(rf"({DECIMAL})%$"),  # ending with a percentage
)


def parse_color_expression(color_text: str) -> tuple[Color, bool]:
    """
    Parses a color expression, such as "red", "#FFCC00", "rgb(1,255,50)", "lime 50%", "95% auto"...

    Args:
        color_text: a color expression supported by ``Color.parse``, optionally prefixed or suffixed with a
            percentage value token.

    Returns:
        tuple[Color, bool]: a Color instance, as well as a boolean telling us if it's a pseudo-color "auto" one.
    """
    alpha = 1.0

    color_text = color_text.strip()

    for alpha_pattern in RE_ALPHA:
        alpha_match = alpha_pattern.search(color_text)
        if alpha_match:
            value = alpha_match.groups()[0]
            alpha_scalar = Scalar.parse(value)
            alpha = alpha_scalar.value / 100.0
            # Ok, let's remove this alpha percentage from the expression before carrying on:
            color_text = alpha_pattern.sub("", color_text).strip()
            break

    if color_text == "auto":
        # For "auto" colors we're still using a Color object, but only to store their alpha.
        # We could use anything for the RGB values since we won't use them, but using (1,2,3) is handy to
        # be able to spot such "I'm just an alpha bearer" Color instances when we debug:
        return Color(1, 2, 3, alpha), True

    color = Color.parse(color_text)
    if alpha < 1:
        color = color.with_alpha(alpha)

    return color, False
