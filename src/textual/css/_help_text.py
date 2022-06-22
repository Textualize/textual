from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Iterable

from textual.color import ColorParseError
from textual.css._help_renderables import Example, Bullet, HelpText
from textual.css.constants import (
    VALID_BORDER,
    VALID_LAYOUT,
    VALID_EDGE,
    VALID_ALIGN_HORIZONTAL,
    VALID_ALIGN_VERTICAL,
    VALID_STYLE_FLAGS,
)

if sys.version_info >= (3, 8):
    from typing import Literal, Iterable, Sequence
else:
    from typing_extensions import Literal

from textual.css._error_tools import friendly_list
from textual.css.scalar import SYMBOL_UNIT

StylingContext = Literal["inline", "css"]
"""The type of styling the user was using when the error was encountered.
Used to give help text specific to the context i.e. we give CSS help if the
user hit an issue with their CSS, and Python help text when the user has an
issue with inline styles."""


@dataclass
class ContextSpecificBullets:
    """
    Args:
        inline (Iterable[Bullet]): Information only relevant to users who are using inline styling.
        css (Iterable[Bullet]): Information only relevant to users who are using CSS.
    """

    inline: Sequence[Bullet]
    css: Sequence[Bullet]

    def get_by_context(self, context: StylingContext) -> list[Bullet]:
        """Get the information associated with the given context

        Args:
            context (StylingContext | None): The context to retrieve info for.
        """
        if context == "inline":
            return list(self.inline)
        else:
            return list(self.css)


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
    property_name: str,
    context: StylingContext,
) -> str:
    """Convert a property name to CSS or inline by replacing
        '-' with '_' or vice-versa

    Args:
        property_name (str): The name of the property
        context (StylingContext): The context the property is being used in.

    Returns:
        str: The property name converted to the given context.
    """
    return _css_name(property_name) if context == "css" else _python_name(property_name)


def _spacing_examples(property_name: str) -> ContextSpecificBullets:
    """Returns examples for spacing properties"""
    return ContextSpecificBullets(
        inline=[
            Bullet(
                f"Set [i]{property_name}[/] to a tuple to assign spacing to each edge",
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
                "Supply 1, 2 or 4 integers separated by a space",
                examples=[
                    Example(f"{property_name}: 1;"),
                    Example(f"{property_name}: 1 2;     [dim]# Vertical, horizontal"),
                    Example(
                        f"{property_name}: 1 2 3 4; [dim]# Top, right, bottom, left"
                    ),
                ],
            ),
        ],
    )


def property_invalid_value_help_text(
    property_name: str, context: StylingContext, *, suggested_property_name: str = None
) -> HelpText:
    """Help text to show when the user supplies an invalid value for CSS property
    property.

    Args:
        property_name (str): The name of the property
        context (StylingContext | None): The context the spacing property is being used in.
    Keyword Args:
        suggested_property_name (str | None): A suggested name for the property (e.g. "width" for "wdth"). Defaults to None.

    Returns:
        HelpText: Renderable for displaying the help text for this property
    """
    property_name = _contextualize_property_name(property_name, context)
    summary = f"Invalid CSS property {property_name!r}"
    if suggested_property_name:
        suggested_property_name = _contextualize_property_name(
            suggested_property_name, context
        )
        summary += f'. Did you mean "{suggested_property_name}"?'
    return HelpText(summary)


def spacing_wrong_number_of_values_help_text(
    property_name: str,
    num_values_supplied: int,
    context: StylingContext,
) -> HelpText:
    """Help text to show when the user supplies the wrong number of values
    for a spacing property (e.g. padding or margin).

    Args:
        property_name (str): The name of the property
        num_values_supplied (int): The number of values the user supplied (a number other than 1, 2 or 4).
        context (StylingContext | None): The context the spacing property is being used in.

    Returns:
        HelpText: Renderable for displaying the help text for this property
    """
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


def spacing_invalid_value_help_text(
    property_name: str,
    context: StylingContext,
) -> HelpText:
    """Help text to show when the user supplies an invalid value for a spacing
    property.

    Args:
        property_name (str): The name of the property
        context (StylingContext | None): The context the spacing property is being used in.

    Returns:
        HelpText: Renderable for displaying the help text for this property
    """
    property_name = _contextualize_property_name(property_name, context)
    return HelpText(
        summary=f"Invalid value for the [i]{property_name}[/] property",
        bullets=_spacing_examples(property_name).get_by_context(context),
    )


def scalar_help_text(
    property_name: str,
    context: StylingContext,
) -> HelpText:
    """Help text to show when the user supplies an invalid value for
    a scalar property.

    Args:
        property_name (str): The name of the property
        num_values_supplied (int): The number of values the user supplied (a number other than 1, 2 or 4).
        context (StylingContext | None): The context the scalar property is being used in.

    Returns:
        HelpText: Renderable for displaying the help text for this property
    """
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
                        "Assign a string, int or Scalar object itself",
                        examples=[
                            Example(f'widget.styles.{property_name} = "50%"'),
                            Example(f"widget.styles.{property_name} = 10"),
                            Example(f"widget.styles.{property_name} = Scalar(...)"),
                        ],
                    ),
                ],
                css=[
                    Bullet(
                        "Write the number followed by the unit",
                        examples=[
                            Example(f"{property_name}: 50%;"),
                            Example(f"{property_name}: 5;"),
                        ],
                    ),
                ],
            ).get_by_context(context),
        ],
    )


def string_enum_help_text(
    property_name: str,
    valid_values: Iterable[str],
    context: StylingContext,
) -> HelpText:
    """Help text to show when the user supplies an invalid value for a string
    enum property.

    Args:
        property_name (str): The name of the property
        valid_values (list[str]): A list of the values that are considered valid.
        context (StylingContext | None): The context the property is being used in.

    Returns:
        HelpText: Renderable for displaying the help text for this property
    """
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
                        "Assign any of the valid strings to the property",
                        examples=[
                            Example(f'widget.styles.{property_name} = "{valid_value}"')
                            for valid_value in sorted(valid_values)
                        ],
                    )
                ],
                css=[
                    Bullet(
                        "Assign any of the valid strings to the property",
                        examples=[
                            Example(f"{property_name}: {valid_value};")
                            for valid_value in sorted(valid_values)
                        ],
                    )
                ],
            ).get_by_context(context),
        ],
    )


def color_property_help_text(
    property_name: str,
    context: StylingContext,
    *,
    error: Exception = None,
) -> HelpText:
    """Help text to show when the user supplies an invalid value for a color
    property. For example, an unparseable color string.

    Args:
        property_name (str): The name of the property
        context (StylingContext | None): The context the property is being used in.
        error (ColorParseError | None): The error that caused this help text to be displayed. Defaults to None.

    Returns:
        HelpText: Renderable for displaying the help text for this property
    """
    property_name = _contextualize_property_name(property_name, context)
    summary = f"Invalid value for the [i]{property_name}[/] property"
    suggested_color = (
        error.suggested_color if error and isinstance(error, ColorParseError) else None
    )
    if suggested_color:
        summary += f'. Did you mean "{suggested_color}"?'
    return HelpText(
        summary=summary,
        bullets=[
            Bullet(
                f"The [i]{property_name}[/] property can only be set to a valid color"
            ),
            Bullet(f"Colors can be specified using hex, RGB, or ANSI color names"),
            *ContextSpecificBullets(
                inline=[
                    Bullet(
                        "Assign colors using strings or Color objects",
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
                        "Colors can be set as follows",
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


def border_property_help_text(property_name: str, context: StylingContext) -> HelpText:
    """Help text to show when the user supplies an invalid value for a border
    property (such as border, border-right, outline)

    Args:
        property_name (str): The name of the property
        context (StylingContext | None): The context the property is being used in.

    Returns:
        HelpText: Renderable for displaying the help text for this property
    """
    property_name = _contextualize_property_name(property_name, context)
    return HelpText(
        summary=f"Invalid value for [i]{property_name}[/] property",
        bullets=[
            *ContextSpecificBullets(
                inline=[
                    Bullet(
                        f"Set [i]{property_name}[/] using a tuple of the form (<bordertype>, <color>)",
                        examples=[
                            Example(
                                f'widget.styles.{property_name} = ("solid", "red")'
                            ),
                            Example(
                                f'widget.styles.{property_name} = ("round", "#f0f0f0")'
                            ),
                            Example(
                                f'widget.styles.{property_name} = [("dashed", "#f0f0f0"), ("solid", "blue")]  [dim]# Vertical, horizontal'
                            ),
                        ],
                    ),
                    Bullet(
                        f"Valid values for <bordertype> are:\n{friendly_list(VALID_BORDER)}"
                    ),
                    Bullet(
                        f"Colors can be specified using hex, RGB, or ANSI color names"
                    ),
                ],
                css=[
                    Bullet(
                        f"Set [i]{property_name}[/] using a value of the form [i]<bordertype> <color>[/]",
                        examples=[
                            Example(f"{property_name}: solid red;"),
                            Example(f"{property_name}: dashed #00ee22;"),
                        ],
                    ),
                    Bullet(
                        f"Valid values for <bordertype> are:\n{friendly_list(VALID_BORDER)}"
                    ),
                    Bullet(
                        f"Colors can be specified using hex, RGB, or ANSI color names"
                    ),
                ],
            ).get_by_context(context),
        ],
    )


def layout_property_help_text(property_name: str, context: StylingContext) -> HelpText:
    """Help text to show when the user supplies an invalid value
    for a layout property.

    Args:
        property_name (str): The name of the property
        context (StylingContext | None): The context the property is being used in.

    Returns:
        HelpText: Renderable for displaying the help text for this property
    """
    property_name = _contextualize_property_name(property_name, context)
    return HelpText(
        summary=f"Invalid value for [i]{property_name}[/] property",
        bullets=[
            Bullet(
                f"The [i]{property_name}[/] property expects a value of {friendly_list(VALID_LAYOUT)}"
            ),
        ],
    )


def docks_property_help_text(property_name: str, context: StylingContext) -> HelpText:
    """Help text to show when the user supplies an invalid value for docks.

    Args:
        property_name (str): The name of the property
        context (StylingContext | None): The context the property is being used in.

    Returns:
        HelpText: Renderable for displaying the help text for this property
    """
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


def dock_property_help_text(property_name: str, context: StylingContext) -> HelpText:
    """Help text to show when the user supplies an invalid value for dock.

    Args:
        property_name (str): The name of the property
        context (StylingContext | None): The context the property is being used in.

    Returns:
        HelpText: Renderable for displaying the help text for this property
    """
    property_name = _contextualize_property_name(property_name, context)
    return HelpText(
        summary=f"Invalid value for [i]{property_name}[/] property",
        bullets=[
            Bullet("The value must be one of the defined docks"),
            *ContextSpecificBullets(
                inline=[
                    Bullet(
                        "Attach a widget to a dock declared on the parent",
                        examples=[
                            Example(
                                f'widget.styles.dock = "left"  [dim] # assumes parent widget has declared left dock[/]'
                            )
                        ],
                    )
                ],
                css=[
                    Bullet(
                        "Define a dock using the [i]docks[/] property",
                        examples=[
                            Example("docks: [u]lhs[/]=left/2;"),
                        ],
                    ),
                    Bullet(
                        "Then attach a widget to a defined dock using the [i]dock[/] property",
                        examples=[
                            Example("dock: [scope.key][u]lhs[/][/];"),
                        ],
                    ),
                ],
            ).get_by_context(context),
        ],
    )


def fractional_property_help_text(
    property_name: str, context: StylingContext
) -> HelpText:
    """Help text to show when the user supplies an invalid value for a fractional property.

    Args:
        property_name (str): The name of the property
        context (StylingContext | None): The context the property is being used in.

    Returns:
        HelpText: Renderable for displaying the help text for this property
    """
    property_name = _contextualize_property_name(property_name, context)
    return HelpText(
        summary=f"Invalid value for [i]{property_name}[/] property",
        bullets=[
            *ContextSpecificBullets(
                inline=[
                    Bullet(
                        f"Set [i]{property_name}[/] to a string or float value",
                        examples=[
                            Example(f'widget.styles.{property_name} = "50%"'),
                            Example(f"widget.styles.{property_name} = 0.25"),
                        ],
                    )
                ],
                css=[
                    Bullet(
                        f"Set [i]{property_name}[/] to a string or float",
                        examples=[
                            Example(f"{property_name}: 50%;"),
                            Example(f"{property_name}: 0.25;"),
                        ],
                    )
                ],
            ).get_by_context(context)
        ],
    )


def offset_property_help_text(context: StylingContext) -> HelpText:
    """Help text to show when the user supplies an invalid value for the offset property.

    Args:
        context (StylingContext | None): The context the property is being used in.

    Returns:
        HelpText: Renderable for displaying the help text for this property
    """
    return HelpText(
        summary="Invalid value for [i]offset[/] property",
        bullets=[
            *ContextSpecificBullets(
                inline=[
                    Bullet(
                        markup="The [i]offset[/] property expects a tuple of 2 values [i](<horizontal>, <vertical>)[/]",
                        examples=[
                            Example("widget.styles.offset = (2, '50%')"),
                        ],
                    ),
                ],
                css=[
                    Bullet(
                        markup="The [i]offset[/] property expects a value of the form [i]<horizontal> <vertical>[/]",
                        examples=[
                            Example(
                                "offset: 2 3;  [dim]# Horizontal offset of 2, vertical offset of 3"
                            ),
                            Example(
                                "offset: 2 50%;  [dim]# Horizontal offset of 2, vertical offset of 50%"
                            ),
                        ],
                    ),
                ],
            ).get_by_context(context),
            Bullet("<horizontal> and <vertical> can be a number or scalar value"),
        ],
    )


def scrollbar_size_property_help_text(context: StylingContext) -> HelpText:
    """Help text to show when the user supplies an invalid value for the scrollbar-size property.

    Args:
        context (StylingContext | None): The context the property is being used in.

    Returns:
        HelpText: Renderable for displaying the help text for this property
    """
    return HelpText(
        summary="Invalid value for [i]scrollbar-size[/] property",
        bullets=[
            *ContextSpecificBullets(
                inline=[
                    Bullet(
                        markup="The [i]scrollbar_size[/] property expects a tuple of 2 values [i](<horizontal>, <vertical>)[/]",
                        examples=[
                            Example("widget.styles.scrollbar_size = (2, 1)"),
                        ],
                    ),
                ],
                css=[
                    Bullet(
                        markup="The [i]scrollbar-size[/] property expects a value of the form [i]<horizontal> <vertical>[/]",
                        examples=[
                            Example(
                                "scrollbar-size: 2 3;  [dim]# Horizontal size of 2, vertical size of 3"
                            ),
                        ],
                    ),
                ],
            ).get_by_context(context),
            Bullet(
                "<horizontal> and <vertical> must be positive integers, greater than zero"
            ),
        ],
    )


def scrollbar_size_single_axis_help_text(property_name: str) -> HelpText:
    """Help text to show when the user supplies an invalid value for a scrollbar-size-* property.

    Args:
        property_name (str): The name of the property

    Returns:
        HelpText: Renderable for displaying the help text for this property
    """
    return HelpText(
        summary=f"Invalid value for [i]{property_name}[/]",
        bullets=[
            Bullet(
                markup=f"The [i]{property_name}[/] property can only be set to a positive integer, greather than zero",
                examples=[
                    Example(f"{property_name}: 2;"),
                ],
            ),
        ],
    )


def align_help_text() -> HelpText:
    """Help text to show when the user supplies an invalid value for a `align`.

    Returns:
        HelpText: Renderable for displaying the help text for this property
    """
    return HelpText(
        summary="Invalid value for [i]align[/] property",
        bullets=[
            Bullet(
                markup="The [i]align[/] property expects exactly 2 values",
                examples=[
                    Example("align: <horizontal> <vertical>"),
                    Example(
                        "align: center middle;  [dim]# Center vertically & horizontally within parent"
                    ),
                    Example(
                        "align: left middle;    [dim]# Align on the middle left of the parent"
                    ),
                ],
            ),
            Bullet(
                f"Valid values for <horizontal> are {friendly_list(VALID_ALIGN_HORIZONTAL)}"
            ),
            Bullet(
                f"Valid values for <vertical> are {friendly_list(VALID_ALIGN_VERTICAL)}",
            ),
        ],
    )


def offset_single_axis_help_text(property_name: str) -> HelpText:
    """Help text to show when the user supplies an invalid value for an offset-* property.

    Args:
        property_name (str): The name of the property

    Returns:
        HelpText: Renderable for displaying the help text for this property
    """
    return HelpText(
        summary=f"Invalid value for [i]{property_name}[/]",
        bullets=[
            Bullet(
                markup=f"The [i]{property_name}[/] property can be set to a number or scalar value",
                examples=[
                    Example(f"{property_name}: 10;"),
                    Example(f"{property_name}: 50%;"),
                ],
            ),
            Bullet(f"Valid scalar units are {friendly_list(SYMBOL_UNIT)}"),
        ],
    )


def style_flags_property_help_text(
    property_name: str, value: str, context: StylingContext
) -> HelpText:
    """Help text to show when the user supplies an invalid value for a style flags property.

    Args:
        property_name (str): The name of the property
        context (StylingContext | None): The context the property is being used in.

    Returns:
        HelpText: Renderable for displaying the help text for this property
    """
    property_name = _contextualize_property_name(property_name, context)
    return HelpText(
        summary=f"Invalid value '{value}' in [i]{property_name}[/] property",
        bullets=[
            Bullet(
                f"Style flag values such as [i]{property_name}[/] expect space-separated values"
            ),
            Bullet(f"Permitted values are {friendly_list(VALID_STYLE_FLAGS)}"),
            *ContextSpecificBullets(
                inline=[
                    Bullet(
                        markup="Supply a string or Style object",
                        examples=[
                            Example(
                                f'widget.styles.{property_name} = "bold italic underline"'
                            )
                        ],
                    ),
                ],
                css=[
                    Bullet(
                        markup="Supply style flags separated by spaces",
                        examples=[Example(f"{property_name}: bold italic underline;")],
                    )
                ],
            ).get_by_context(context),
        ],
    )
