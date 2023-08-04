"""Provides the HorizontalRule and VerticalRule widgets. These widgets are similar to the <hr> HTML tag."""

from __future__ import annotations

from abc import abstractmethod

from rich.text import Text
from textual.app import RenderResult
from textual.css.types import EdgeType as LineStyle
from textual.widget import Widget


# Followed the same pattern as the other widgets in the package, so we can lazy load them.
__all__ = [
    "HorizontalRule",
    "VerticalRule",
]

DEFAULT_LINE_STYLE = 'solid'
DEFAULT_LENGTH_FACTOR = 0.8


class Rule(Widget, can_focus=False):
    """A base rule widget, providing common functionality for HorizontalRule and VerticalRule"""

    DEFAULT_CSS = """
    Rule {
        color: $panel;
    }
    """
    STYLES: dict[LineStyle, str] = {}
    """A dictionary mapping line types to the character used for drawing the line."""

    line_style: LineStyle
    """The style of the line. Default is 'solid'."""
    length_factor: float
    """The length factor of the line. Should be between 0 and 1. 0 means no line, 1 means full line. Default is 0.8."""

    def __init__(
        self,
        line_style: LineStyle = DEFAULT_LINE_STYLE,
        length_factor: float = DEFAULT_LENGTH_FACTOR,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ):
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self.line_style = line_style
        self.length_factor = self._validate_length_factor(length_factor)

    def _validate_length_factor(self, length_factor: float) -> float:
        """Validate the length factor.

        The length factor should be between 0 and 1. If it's not, raise ValueError.
        """
        if 0 <= length_factor <= 1:
            return length_factor
        else:
            raise ValueError("length_factor should be a value between 0 and 1.")

    @abstractmethod
    @property
    def rule_extent(self) -> int:
        """Abstract property to be implemented by subclasses.

        Must return the maximum extent (width or height) for the rule.
        """
        raise NotImplementedError

    @property
    def rule_drawn_extent(self) -> int:
        """Return the length of the rule to be drawn, based on the length factor."""
        return int(self.length_factor * self.rule_extent)

    @property
    def rule_symbol(self) -> str:
        """Return the symbol used for drawing the rule"""
        return self.STYLES[self.line_style]

    def render(self) -> RenderResult:
        """Renders the rule widget.

        It does so by creating a line using the symbol for the specified length, and adding necessary padding.
        """
        padding_length = self._calculate_padding_length()
        padding = ' ' * padding_length
        rule = self.rule_symbol * self.rule_drawn_extent
        return Text(padding + rule + padding)

    def _calculate_padding_length(self) -> int:
        """Calculate the padding length to center the line."""
        return (self.rule_extent - self.rule_drawn_extent) // 2


class HorizontalRule(Rule):
    """A horizontal line widget, similar to a <hr> HTML tag."""

    DEFAULT_CSS = """
    HorizontalRule {
        height: 1;
        margin: 1 0;
    }
    """
    STYLES: dict[LineStyle, str] = {
        "": " ",
        "ascii": "-",
        "none": " ",
        "hidden": " ",
        "blank": " ",
        "round": "─",
        "solid": "─",
        "double": "═",
        "dashed": "╍",
        "heavy": "━",
        "inner": "▄",
        "outer": "▀",
        "thick": "▀",
        "hkey": "▔",
        "vkey": " ",
        "tall": "▔",
        "panel": "█",
        "wide": "▁",
    }
    """A dictionary mapping line types to the character used for drawing the line."""

    def rule_extent(self) -> int:
        """Return the width of the widget for horizontal rules."""
        return self.size.width


class VerticalRule(Rule):
    """A vertical line widget, similar to a <hr> HTML tag, except it's vertical."""

    DEFAULT_CSS = """
    VerticalRule {
        width: 1;
        margin: 0 2;
    }
    """
    STYLES: dict[LineStyle, str] = {
        "": " ",
        "ascii": "|",
        "none": " ",
        "hidden": " ",
        "blank": " ",
        "round": "│",
        "solid": "│",
        "double": "║",
        "dashed": "╏",
        "heavy": "┃",
        "inner": "▐",
        "outer": "▌",
        "thick": "█",
        "hkey": " ",
        "vkey": "▏",
        "tall": "▊",
        "panel": "▊",
        "wide": "▎",
    }
    """A dictionary mapping line types to the character used for drawing the line."""

    def rule_extent(self) -> int:
        """Return the height of the widget for vertical rules."""
        return self.size.height
