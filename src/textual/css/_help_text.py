from textual.css._error_tools import friendly_list
from textual.css.scalar import SYMBOL_UNIT


def _inline_name(property_name: str) -> str:
    return property_name.replace("-", "_")


def spacing_help_text(property_name: str, num_values_supplied: int) -> str:
    return f"""\
• You supplied {num_values_supplied} values for the '{property_name}' property
• Spacing properties like 'margin' and 'padding' require either 1, 2 or 4 integer values
• In Textual CSS, supply 1, 2 or 4 values separated by a space
    [dim]e.g. [/][i]{property_name}: 1 2 3 4;[/]
• In Python, you can set it to a tuple to assign spacing to each edge
    [dim]e.g. [/][i]widget.styles.{_inline_name(property_name)} = (1, 2, 3, 4)[/]
• Or to an integer to assign to all edges at once
    [dim]e.g. [/][i]widget.styles.{_inline_name(property_name)} = 2[/]"""


def scalar_help_text(property_name: str) -> str:
    return f"""\
• Invalid value for the '{property_name}' property
• Scalar properties like '{property_name}' require numerical values and an optional unit
• Valid units are {friendly_list(SYMBOL_UNIT)}
• Here's an example of how you'd set a scalar property in Textual CSS
    [dim]e.g. [/][i]{property_name}: 50%;[/]
• In Python, you can assign a string, int or Scalar object itself
    [dim]e.g. [/][i]widget.styles.{_inline_name(property_name)} = "50%"[/]
    [dim]e.g. [/][i]widget.styles.{_inline_name(property_name)} = 10[/]
    [dim]e.g. [/][i]widget.styles.{_inline_name(property_name)} = Scalar(...)[/]"""
