from __future__ import annotations

import itertools
import sys

from textual.css._help_renderables import Example, Bullet, HelpText

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal

if sys.version_info >= (3, 9):
    from typing import Annotated
else:
    from typing_extensions import Annotated

from textual.css._error_tools import friendly_list
from textual.css.scalar import SYMBOL_UNIT

StylingStrategy = Annotated[
    Literal["inline", "css"],
    """The type of styling the user was using when the error was encountered.
Used to give help text specific to the context i.e. we give CSS help if the
user hit an issue with their CSS, and Python help text when the user has an
issue with inline styles.""",
]


def _python_name(property_name: str) -> str:
    """Convert a CSS property name to the corresponding Python attribute name

    Args:
        property_name (str): The CSS property name

    Returns:
        str: The Python attribute name as found on the Styles object
    """
    return property_name.replace("-", "_")


def spacing_help_text(
    property_name: str,
    num_values_supplied: int,
    strategy: StylingStrategy | None = None,
) -> HelpText:
    context_specific_bullets = {
        "inline": (
            Bullet(
                "In Python, you can set it to a tuple to assign spacing to each edge",
                examples=[
                    Example(
                        f"widget.styles.{_python_name(property_name)} = (1, 2) [dim]# Vertical, horizontal"
                    ),
                    Example(
                        f"widget.styles.{_python_name(property_name)} = (1, 2, 3, 4) [dim]# Top, right, bottom, left"
                    ),
                ],
            ),
            Bullet(
                "Or to an integer to assign a single value to all edges",
                examples=[Example(f"widget.styles.{_python_name(property_name)} = 2")],
            ),
        ),
        "css": (
            Bullet(
                "In Textual CSS, supply 1, 2 or 4 values separated by a space",
                examples=[
                    Example(f"{property_name}: 1;"),
                    Example(f"{property_name}: 1 2; [dim]# Vertical, horizontal"),
                    Example(
                        f"{property_name}: 1 2 3 4; [dim]# Top, right, bottom, left"
                    ),
                ],
            ),
        ),
    }

    context_bullets = (
        context_specific_bullets.get(strategy, [])
        if strategy
        else itertools.chain.from_iterable(context_specific_bullets.values())
    )

    return HelpText(
        Bullet(
            f"You supplied {num_values_supplied} values for the '{property_name}' property"
        ),
        Bullet(
            "Spacing properties like 'margin' and 'padding' require either 1, 2 or 4 integer values"
        ),
        *context_bullets,
    )


def scalar_help_text(property_name: str) -> HelpText:
    return f"""\
• Invalid value for the '{property_name}' property
• Scalar properties like '{property_name}' require numerical values and an optional unit
• Valid units are {friendly_list(SYMBOL_UNIT)}
• Here's an example of how you'd set a scalar property in Textual CSS
    [dim]e.g. [/][i]{property_name}: 50%;[/]
• In Python, you can assign a string, int or Scalar object itself
    [dim]e.g. [/][i]widget.styles.{_python_name(property_name)} = "50%"[/]
    [dim]e.g. [/][i]widget.styles.{_python_name(property_name)} = 10[/]
    [dim]e.g. [/][i]widget.styles.{_python_name(property_name)} = Scalar(...)[/]"""
