"""
Helper functions to work with Textual Colors.
"""

from __future__ import annotations

from textual.color import Color
from textual.css._help_text import color_property_help_text
from textual.css.errors import DeclarationError, StyleValueError
from textual.css.scalar import Scalar, Unit
from textual.css.tokenizer import Token


def parse_color_tokens(property_name: str, tokens: list[Token]) -> tuple[Color, bool]:
    """
    Parses the tokens of a color expression, such as "red", "#FFCC00", "rgb(1,255,50)", "lime 50%", "95% auto"...

    Args:
        property_name (str): The name of the CSS property. Only used to raise DeclarationErrors that include this name.
        tokens (list[Token]): CSS tokens describing a color - i.e. an expression supported by ``Color.parse``,
            optionally prefixed or suffixed with a percentage value token.

    Returns:
        tuple[Color, bool]: a Color instance, as well as a boolean telling us if it's a pseudo-color "auto" one.

    Raises:
        DeclarationError: if we come across an unexpected value
    """
    property_name = property_name.replace("-", "_")

    alpha = 1.0
    color = None
    is_auto = False

    for token in tokens:
        if token.name == "token" and token.value == "auto":
            is_auto = True
        elif token.name == "scalar":
            alpha_scalar = Scalar.parse(token.value)
            if alpha_scalar.unit != Unit.PERCENT:
                raise DeclarationError(
                    property_name, token, "alpha must be given as a percentage."
                )
            alpha = alpha_scalar.value / 100.0
        elif token.name in ("color", "token"):
            try:
                color = Color.parse(token.value)
            except Exception as error:
                raise DeclarationError(
                    property_name,
                    token,
                    color_property_help_text(property_name, context="css", error=error),
                )
        elif token.name == "whitespace":
            continue
        else:
            raise DeclarationError(
                property_name,
                token,
                color_property_help_text(property_name, context="css"),
            )

    if is_auto:
        # For "auto" colors we're still using a Color object, but only to store their alpha.
        # We could use anything for the RGB values since we won't use them, but using (1,2,3) is handy to
        # be able to spot such "I'm just an alpha bearer" Color instances when we debug:
        return Color(1, 2, 3, alpha), True

    if color is None:
        raise StyleValueError(
            f"no Color could be extracted from the given expression for property '{property_name}'."
        )

    if alpha is not None and alpha < 1:
        color = color.with_alpha(alpha)

    return color, False
