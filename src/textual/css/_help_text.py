from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from typing_extensions import Literal

from textual.color import ColorParseError
from textual.css._error_tools import friendly_list
from textual.css._help_renderables import Bullet, Example, HelpText
from textual.css.constants import (
    VALID_ALIGN_HORIZONTAL,
    VALID_ALIGN_VERTICAL,
    VALID_BORDER,
    VALID_EXPAND,
    VALID_KEYLINE,
    VALID_LAYOUT,
    VALID_POSITION,
    VALID_STYLE_FLAGS,
    VALID_TEXT_ALIGN,
)
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
        inline: Information only relevant to users who are using inline styling.
        css: Information only relevant to users who are using CSS.
    """

    inline: Sequence[Bullet]
    css: Sequence[Bullet]

    def get_by_context(self, context: StylingContext) -> list[Bullet]:
        """Get the information associated with the given context

        Args:
            context: The context to retrieve info for.
        """
        if context == "inline":
            return list(self.inline)
        else:
            return list(self.css)


def _python_name(property_name: str) -> str:
    """Convert a CSS property name to the corresponding Python attribute name

    Args:
        property_name: The CSS property name

    Returns:
        The Python attribute name as found on the Styles object
    """
    return property_name.replace("-", "_")


def _css_name(property_name: str) -> str:
    """Convert a Python style attribute name to the corresponding CSS property name

    Args:
        property_name: The Python property name

    Returns:
        The CSS property name
    """
    return property_name.replace("_", "-")


def _contextualize_property_name(
    property_name: str,
    context: StylingContext,
) -> str:
    """Convert a property name to CSS or inline by replacing
        '-' with '_' or vice-versa

    Args:
        property_name: The name of the property
        context: The context the property is being used in.

    Returns:
        The property name converted to the given context.
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
    property_name: str,
    context: StylingContext,
    *,
    suggested_property_name: str | None = None,
) -> HelpText:
    """Help text to show when the user supplies an invalid value for CSS property
    property.

    Args:
        property_name: The name of the property.
        context: The context the spacing property is being used in.
    Keyword Args:
        suggested_property_name: A suggested name for the property (e.g. "width" for "wdth").

    Returns:
        Renderable for displaying the help text for this property.
    """
    property_name = _contextualize_property_name(property_name, context)
    summary = f"Invalid CSS property {property_name!r}"
    if suggested_property_name:
        suggested_property_name = _contextualize_property_name(
            suggested_property_name, context
        )
        summary += f". Did you mean '{suggested_property_name}'?"
    return HelpText(summary)


def spacing_wrong_number_of_values_help_text(
    property_name: str,
    num_values_supplied: int,
    context: StylingContext,
) -> HelpText:
    """Help text to show when the user supplies the wrong number of values
    for a spacing property (e.g. padding or margin).

    Args:
        property_name: The name of the property.
        num_values_supplied: The number of values the user supplied (a number other than 1, 2 or 4).
        context: The context the spacing property is being used in.

    Returns:
        Renderable for displaying the help text for this property.
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
        property_name: The name of the property.
        context: The context the spacing property is being used in.

    Returns:
        Renderable for displaying the help text for this property.
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
        property_name: The name of the property.
        num_values_supplied: The number of values the user supplied (a number other than 1, 2 or 4).
        context: The context the scalar property is being used in.

    Returns:
        Renderable for displaying the help text for this property.
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
        property_name: The name of the property.
        valid_values: A list of the values that are considered valid.
        context: The context the property is being used in.

    Returns:
        Renderable for displaying the help text for this property.
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
    error: Exception | None = None,
    value: str | None = None,
) -> HelpText:
    """Help text to show when the user supplies an invalid value for a color
    property. For example, an unparsable color string.

    Args:
        property_name: The name of the property.
        context: The context the property is being used in.
        error: The error that caused this help text to be displayed.

    Returns:
        Renderable for displaying the help text for this property.
    """
    property_name = _contextualize_property_name(property_name, context)
    if value is None:
        summary = f"Invalid value for the [i]{property_name}[/] property"
    else:
        summary = f"Invalid value ({value!r}) for the [i]{property_name}[/] property"
    suggested_color = (
        error.suggested_color if error and isinstance(error, ColorParseError) else None
    )
    if suggested_color:
        summary += f". Did you mean '{suggested_color}'?"
    return HelpText(
        summary=summary,
        bullets=[
            Bullet(
                f"The [i]{property_name}[/] property can only be set to a valid color"
            ),
            Bullet("Colors can be specified using hex, RGB, or ANSI color names"),
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
    property (such as border, border-right, outline).

    Args:
        property_name: The name of the property.
        context: The context the property is being used in.

    Returns:
        Renderable for displaying the help text for this property.
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
                        "Colors can be specified using hex, RGB, or ANSI color names"
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
                        "Colors can be specified using hex, RGB, or ANSI color names"
                    ),
                ],
            ).get_by_context(context),
        ],
    )


def layout_property_help_text(property_name: str, context: StylingContext) -> HelpText:
    """Help text to show when the user supplies an invalid value
    for a layout property.

    Args:
        property_name: The name of the property.
        context: The context the property is being used in.

    Returns:
        Renderable for displaying the help text for this property.
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


def dock_property_help_text(property_name: str, context: StylingContext) -> HelpText:
    """Help text to show when the user supplies an invalid value for dock.

    Args:
        property_name: The name of the property.
        context: The context the property is being used in.

    Returns:
        Renderable for displaying the help text for this property.
    """
    property_name = _contextualize_property_name(property_name, context)
    return HelpText(
        summary=f"Invalid value for [i]{property_name}[/] property",
        bullets=[
            Bullet(
                "The value must be one of 'top', 'right', 'bottom', 'left' or 'none'"
            ),
            *ContextSpecificBullets(
                inline=[
                    Bullet(
                        "The 'dock' rule attaches a widget to the edge of a container.",
                        examples=[Example('header.styles.dock = "top"')],
                    )
                ],
                css=[
                    Bullet(
                        "The 'dock' rule attaches a widget to the edge of a container.",
                        examples=[Example("dock: top")],
                    )
                ],
            ).get_by_context(context),
        ],
    )


def split_property_help_text(property_name: str, context: StylingContext) -> HelpText:
    """Help text to show when the user supplies an invalid value for split.

    Args:
        property_name: The name of the property.
        context: The context the property is being used in.

    Returns:
        Renderable for displaying the help text for this property.
    """
    property_name = _contextualize_property_name(property_name, context)
    return HelpText(
        summary=f"Invalid value for [i]{property_name}[/] property",
        bullets=[
            Bullet("The value must be one of 'top', 'right', 'bottom' or 'left'"),
            *ContextSpecificBullets(
                inline=[
                    Bullet(
                        "The 'split' splits the container and aligns the widget to the given edge.",
                        examples=[Example('header.styles.split = "top"')],
                    )
                ],
                css=[
                    Bullet(
                        "The 'split' splits the container and aligns the widget to the given edge.",
                        examples=[Example("split: top")],
                    )
                ],
            ).get_by_context(context),
        ],
    )


def fractional_property_help_text(
    property_name: str, context: StylingContext
) -> HelpText:
    """Help text to show when the user supplies an invalid value for a fractional property.

    Args:
        property_name: The name of the property.
        context: The context the property is being used in.

    Returns:
        Renderable for displaying the help text for this property.
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
        context: The context the property is being used in.

    Returns:
        Renderable for displaying the help text for this property.
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
        context: The context the property is being used in.

    Returns:
        Renderable for displaying the help text for this property.
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
            Bullet("<horizontal> and <vertical> must be non-negative integers."),
        ],
    )


def scrollbar_size_single_axis_help_text(property_name: str) -> HelpText:
    """Help text to show when the user supplies an invalid value for a scrollbar-size-* property.

    Args:
        property_name: The name of the property.

    Returns:
        Renderable for displaying the help text for this property.
    """
    return HelpText(
        summary=f"Invalid value for [i]{property_name}[/]",
        bullets=[
            Bullet(
                markup=f"The [i]{property_name}[/] property can only be set to a positive integer, greater than zero",
                examples=[
                    Example(f"{property_name}: 2;"),
                ],
            ),
        ],
    )


def integer_help_text(property_name: str) -> HelpText:
    """Help text to show when the user supplies an invalid integer value.

    Args:
        property_name: The name of the property.

    Returns:
        Renderable for displaying the help text for this property.
    """
    return HelpText(
        summary=f"Invalid value for [i]{property_name}[/]",
        bullets=[
            Bullet(
                markup="An integer value is expected here",
                examples=[
                    Example(f"{property_name}: 2;"),
                ],
            ),
        ],
    )


def align_help_text() -> HelpText:
    """Help text to show when the user supplies an invalid value for a `align`.

    Returns:
        Renderable for displaying the help text for this property.
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


def keyline_help_text() -> HelpText:
    """Help text to show when the user supplies an invalid value for a `keyline`.

    Returns:
        Renderable for displaying the help text for this property.
    """
    return HelpText(
        summary="Invalid value for [i]keyline[/] property",
        bullets=[
            Bullet(
                markup="The [i]keyline[/] property expects exactly 2 values",
                examples=[
                    Example("keyline: <type> <color>"),
                ],
            ),
            Bullet(f"Valid values for <type> are {friendly_list(VALID_KEYLINE)}"),
        ],
    )


def text_align_help_text() -> HelpText:
    """Help text to show when the user supplies an invalid value for the text-align property.

    Returns:
        Renderable for displaying the help text for this property.
    """
    return HelpText(
        summary="Invalid value for the [i]text-align[/] property.",
        bullets=[
            Bullet(
                f"The [i]text-align[/] property must be one of {friendly_list(VALID_TEXT_ALIGN)}",
                examples=[
                    Example("text-align: center;"),
                    Example("text-align: right;"),
                ],
            )
        ],
    )


def offset_single_axis_help_text(property_name: str) -> HelpText:
    """Help text to show when the user supplies an invalid value for an offset-* property.

    Args:
        property_name: The name of the property.

    Returns:
        Renderable for displaying the help text for this property.
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


def position_help_text(property_name: str) -> HelpText:
    """Help text to show when the user supplies the wrong value for position.

    Args:
        property_name: The name of the property.

    Returns:
        Renderable for displaying the help text for this property.
    """
    return HelpText(
        summary=f"Invalid value for [i]{property_name}[/]",
        bullets=[
            Bullet(f"Valid values are {friendly_list(VALID_POSITION)}"),
        ],
    )


def expand_help_text(property_name: str) -> HelpText:
    """Help text to show when the user supplies the wrong value for expand.

    Args:
        property_name: The name of the property.

    Returns:
        Renderable for displaying the help text for this property.
    """
    return HelpText(
        summary=f"Invalid value for [i]{property_name}[/]",
        bullets=[
            Bullet(f"Valid values are {friendly_list(VALID_EXPAND)}"),
        ],
    )


def style_flags_property_help_text(
    property_name: str, value: str, context: StylingContext
) -> HelpText:
    """Help text to show when the user supplies an invalid value for a style flags property.

    Args:
        property_name: The name of the property.
        context: The context the property is being used in.

    Returns:
        Renderable for displaying the help text for this property.
    """
    property_name = _contextualize_property_name(property_name, context)
    return HelpText(
        summary=f"Invalid value '{value}' in [i]{property_name}[/] property",
        bullets=[
            Bullet(
                f"Style flag values such as [i]{property_name}[/] expect space-separated values"
            ),
            Bullet(f"Permitted values are {friendly_list(VALID_STYLE_FLAGS)}"),
            Bullet("The value 'none' cannot be mixed with others"),
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


def table_rows_or_columns_help_text(
    property_name: str, value: str, context: StylingContext
):
    property_name = _contextualize_property_name(property_name, context)
    return HelpText(
        summary=f"Invalid value '{value}' in [i]{property_name}[/] property"
    )
