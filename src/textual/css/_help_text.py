from __future__ import annotations

import sys
from dataclasses import dataclass

from textual.css._help_renderables import Example, Bullet, HelpText
from textual.css.constants import VALID_BORDER, VALID_LAYOUT, VALID_EDGE

if sys.version_info >= (3, 8):
    from typing import Literal, Iterable
else:
    from typing_extensions import Literal

if sys.version_info >= (3, 9):
    from typing import Annotated
else:
    from typing_extensions import Annotated

from textual.css._error_tools import friendly_list
from textual.css.scalar import SYMBOL_UNIT

StylingContext = Annotated[
    Literal["inline", "css"],
    """The type of styling the user was using when the error was encountered.
Used to give help text specific to the context i.e. we give CSS help if the
user hit an issue with their CSS, and Python help text when the user has an
issue with inline styles.""",
]


@dataclass
class ContextSpecificBullets:
    inline: Iterable[Bullet]
    css: Iterable[Bullet]

    def get_by_context(self, context: StylingContext | None) -> list[Bullet]:
        if context == "inline":
            return list(self.inline)
        elif context == "css":
            return list(self.css)
        else:
            return list(self.inline) + list(self.css)


def _python_name(property_name: str) -> str:
    """Convert a CSS property name to the corresponding Python attribute name

    Args:
        property_name (str): The CSS property name

    Returns:
        str: The Python attribute name as found on the Styles object
    """
    return property_name.replace("-", "_")


def _css_name(property_name: str) -> str:
    """Convert a Python style attribute name to the corresponding CSS property name

    Args:
        property_name (str): The Python property name

    Returns:
        str: The CSS property name
    """
    return property_name.replace("_", "-")


def _contextualize_property_name(
    property_name: str, context: StylingContext | None
) -> str:
    if context:
        return (
            _css_name(property_name)
            if context == "css"
            else _python_name(property_name)
        )
    return property_name


def _spacing_examples(property_name: str) -> ContextSpecificBullets:
    return ContextSpecificBullets(
        inline=[
            Bullet(
                "In Python, you can set it to a tuple to assign spacing to each edge",
                examples=[
                    Example(
                        f"widget.styles.{property_name} = (1, 2) [dim]# Vertical, horizontal"
                    ),
                    Example(
                        f"widget.styles.{property_name} = (1, 2, 3, 4) [dim]# Top, right, bottom, left"
                    ),
                ],
            ),
            Bullet(
                "Or to an integer to assign a single value to all edges",
                examples=[Example(f"widget.styles.{property_name} = 2")],
            ),
        ],
        css=[
            Bullet(
                "In Textual CSS, supply 1, 2 or 4 integers separated by a space",
                examples=[
                    Example(f"{property_name}: 1;"),
                    Example(f"{property_name}: 1 2; [dim]# Vertical, horizontal"),
                    Example(
                        f"{property_name}: 1 2 3 4; [dim]# Top, right, bottom, left"
                    ),
                ],
            ),
        ],
    )


def spacing_wrong_number_of_values(
    property_name: str,
    num_values_supplied: int,
    context: StylingContext | None = None,
) -> HelpText:
    property_name = _contextualize_property_name(property_name, context)
    return HelpText(
        summary=f"Invalid number of values for the [i]{property_name}[/] property",
        bullets=[
            Bullet(
                f"You supplied {num_values_supplied} values for the [i]{property_name}[/] property"
            ),
            Bullet(
                "Spacing properties like [i]margin[/] and [i]padding[/] require either 1, 2 or 4 integer values"
            ),
            *_spacing_examples(property_name).get_by_context(context),
        ],
    )


def spacing_invalid_value(
    property_name: str, context: StylingContext | None = None
) -> HelpText:
    property_name = _contextualize_property_name(property_name, context)
    return HelpText(
        summary=f"Invalid value for the [i]{property_name}[/] property",
        bullets=_spacing_examples(property_name).get_by_context(context),
    )


def scalar_help_text(
    property_name: str, context: StylingContext | None = None
) -> HelpText:
    property_name = _contextualize_property_name(property_name, context)
    return HelpText(
        summary=f"Invalid value for the [i]{property_name}[/] property",
        bullets=[
            Bullet(
                f"Scalar properties like [i]{property_name}[/] require numerical values and an optional unit"
            ),
            Bullet(f"Valid units are {friendly_list(SYMBOL_UNIT)}"),
            *ContextSpecificBullets(
                inline=[
                    Bullet(
                        "In Python, you can assign a string, int or Scalar object itself",
                        examples=[
                            Example(f'widget.styles.{property_name} = "50%"'),
                            Example(f"widget.styles.{property_name} = 10"),
                            Example(f"widget.styles.{property_name} = Scalar(...)"),
                        ],
                    ),
                ],
                css=[
                    Bullet(
                        "In Textual CSS, write the number followed by the unit",
                        examples=[Example(f"{property_name}: 50%;")],
                    ),
                ],
            ).get_by_context(context),
        ],
    )


def string_enum_help_text(
    property_name: str, valid_values: list[str], context: StylingContext | None = None
) -> HelpText:
    property_name = _contextualize_property_name(property_name, context)
    return HelpText(
        summary=f"Invalid value for the [i]{property_name}[/] property",
        bullets=[
            Bullet(
                f"The [i]{property_name}[/] property can only be set to {friendly_list(valid_values)}"
            ),
            *ContextSpecificBullets(
                inline=[
                    Bullet(
                        "In Python, you can assign any of the valid strings to the property",
                        examples=[
                            Example(f'widget.styles.{property_name} = "{valid_value}"')
                            for valid_value in valid_values
                        ],
                    )
                ],
                css=[
                    Bullet(
                        "In Textual CSS, you can assign any of the valid strings to the property",
                        examples=[
                            Example(f"{property_name}: {valid_value};")
                            for valid_value in valid_values
                        ],
                    )
                ],
            ).get_by_context(context),
        ],
    )


def color_property_help_text(
    property_name: str, context: StylingContext | None = None
) -> HelpText:
    property_name = _contextualize_property_name(property_name, context)
    return HelpText(
        summary=f"Invalid value for the [i]{property_name}[/] property",
        bullets=[
            Bullet(
                f"The [i]{property_name}[/] property can only be set to a valid color"
            ),
            Bullet(f"Colors can be specified using hex, RGB, or ANSI color names"),
            *ContextSpecificBullets(
                inline=[
                    Bullet(
                        "In Python, you can assign colors using strings or Color objects",
                        examples=[
                            Example(f'widget.styles.{property_name} = "#ff00aa"'),
                            Example(
                                f'widget.styles.{property_name} = "rgb(12,231,45)"'
                            ),
                            Example(f'widget.styles.{property_name} = "red"'),
                            Example(
                                f"widget.styles.{property_name} = Color(1, 5, 29, a=0.5)"
                            ),
                        ],
                    )
                ],
                css=[
                    Bullet(
                        "In Textual CSS, colors can be set as follows",
                        examples=[
                            Example(f"{property_name}: [#ff00aa]#ff00aa[/];"),
                            Example(f"{property_name}: rgb(12,231,45);"),
                            Example(f"{property_name}: [rgb(255,0,0)]red[/];"),
                        ],
                    )
                ],
            ).get_by_context(context),
        ],
    )


def border_property_help_text(
    property_name: str, context: StylingContext | None
) -> HelpText:
    property_name = _contextualize_property_name(property_name, context)
    return HelpText(
        summary=f"Invalid value for [i]{property_name}[/] property",
        bullets=[
            *ContextSpecificBullets(
                inline=[
                    Bullet(
                        f"In Python, set [i]{property_name}[/] using a tuple of the form (<bordertype>, <color>)",
                        examples=[
                            Example(
                                f'widget.styles.{property_name} = ("solid", "red")'
                            ),
                            Example(
                                f'widget.styles.{property_name} = ("round", #f0f0f0")'
                            ),
                            Example(
                                f'widget.styles.{property_name} = [("dashed", "#f0f0f0"), ("solid", "blue")]  [dim]# Vertical, horizontal'
                            ),
                        ],
                    ),
                    Bullet(
                        f"Valid values for <bordertype> are:\n  {friendly_list(VALID_BORDER)}"
                    ),
                    Bullet(
                        f"Colors can be specified using hex, RGB, or ANSI color names"
                    ),
                ],
                css=[
                    Bullet(
                        f"In Textual CSS, set [i]{property_name}[/] using a value of the form [i]<bordertype> <color>[/]",
                        examples=[
                            Example(f"{property_name}: solid red;"),
                            Example(f"{property_name}: dashed #00ee22;"),
                        ],
                    ),
                    Bullet(
                        f"Valid values for <bordertype> are:\n  {friendly_list(VALID_BORDER)}"
                    ),
                    Bullet(
                        f"Colors can be specified using hex, RGB, or ANSI color names"
                    ),
                ],
            ).get_by_context(context),
        ],
    )


def layout_property_help_text(
    property_name: str, context: StylingContext | None
) -> HelpText:
    property_name = _contextualize_property_name(property_name, context)
    return HelpText(
        summary=f"Invalid value for [i]{property_name}[/] property",
        bullets=[
            Bullet(
                f"The [i]{property_name}[/] property expects a value of {friendly_list(VALID_LAYOUT)}"
            ),
        ],
    )


def docks_property_help_text(
    property_name: str, context: StylingContext | None
) -> HelpText:
    property_name = _contextualize_property_name(property_name, context)
    return HelpText(
        summary=f"Invalid value for [i]{property_name}[/] property",
        bullets=[
            *ContextSpecificBullets(
                inline=[
                    Bullet(
                        f"The [i]{property_name}[/] property expects an iterable of DockGroups",
                        examples=[
                            Example(
                                f"widget.styles.{property_name} = [DockGroup(...), DockGroup(...)]"
                            )
                        ],
                    ),
                ],
                css=[
                    Bullet(
                        f"The [i]{property_name}[/] property expects a value of the form <name>=<edge>/<zindex>...",
                        examples=[
                            Example(
                                f"{property_name}: lhs=left/2;  [dim]# dock named [u]lhs[/], on [u]left[/] edge, with z-index [u]2[/]"
                            ),
                            Example(
                                f"{property_name}: top=top/3 rhs=right/2;  [dim]# declaring multiple docks"
                            ),
                        ],
                    ),
                    Bullet("<name> can be any string you want"),
                    Bullet(f"<edge> must be one of {friendly_list(VALID_EDGE)}"),
                    Bullet(f"<zindex> must be an integer"),
                ],
            ).get_by_context(context)
        ],
    )
