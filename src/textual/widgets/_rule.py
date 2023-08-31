from __future__ import annotations

from rich.text import Text
from typing_extensions import Literal

from .._border import BORDER_CHARS
from ..app import RenderResult
from ..css._error_tools import friendly_list
from ..css.constants import VALID_BORDER
from ..css.types import EdgeType
from ..reactive import Reactive, reactive
from ..widget import Widget

RuleOrientation = Literal["horizontal", "vertical"]

LineStyle = EdgeType


_VALID_RULE_ORIENTATIONS = {"horizontal", "vertical"}
"""The valid orientations of the rule widget"""

_VALID_LINE_STYLES = VALID_BORDER
"""The valid line styles of the rule widget"""


class InvalidRuleOrientation(Exception):
    """Exception raised for an invalid rule orientation."""


class InvalidLineStyle(Exception):
    """Exception raised for an invalid rule line style."""


class Rule(Widget, can_focus=False):
    """A rule widget to separate content, similar to a <hr> HTML tag."""

    DEFAULT_CSS = """
    Rule {
        color: $primary;
    }

    Rule.-horizontal {
        max-height: 1;
        margin: 1 0;
    }

    Rule.-vertical {
        max-width: 1;
        margin: 0 2;
    }
    """

    orientation: Reactive[RuleOrientation] = reactive[RuleOrientation]("horizontal")
    """The orientation of the rule."""

    line_style: Reactive[LineStyle] = reactive[LineStyle]("solid")
    """The line style of the rule."""

    def __init__(
        self,
        orientation: RuleOrientation = "horizontal",
        line_style: LineStyle = "solid",
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        """Initialize a rule widget.

        Args:
            orientation: The orientation of the rule.
            line_style: The line style of the rule.
            name: The name of the widget.
            id: The ID of the widget in the DOM.
            classes: The CSS classes of the widget.
            disabled: Whether the widget is disabled or not.
        """
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self.orientation = orientation
        self.line_style = line_style

    def render(self) -> RenderResult:
        rule_char: str
        if self.orientation == "vertical":
            rule_char = BORDER_CHARS[self.line_style][1][0]  # middle-left border char
            return Text(rule_char * self.size.height)
        elif self.orientation == "horizontal":
            rule_char = BORDER_CHARS[self.line_style][0][1]  # top-middle border char
            return Text(rule_char * self.size.width)
        else:
            raise InvalidRuleOrientation(
                f"Valid rule orientations are {friendly_list(_VALID_RULE_ORIENTATIONS)}"
            )

    def watch_orientation(
        self, old_orientation: RuleOrientation, orientation: RuleOrientation
    ) -> None:
        self.remove_class(f"-{old_orientation}")
        self.add_class(f"-{orientation}")

    def validate_orientation(self, orientation: RuleOrientation) -> RuleOrientation:
        if orientation not in _VALID_RULE_ORIENTATIONS:
            raise InvalidRuleOrientation(
                f"Valid rule orientations are {friendly_list(_VALID_RULE_ORIENTATIONS)}"
            )
        return orientation

    def validate_line_style(self, style: LineStyle) -> LineStyle:
        if style not in _VALID_LINE_STYLES:
            raise InvalidLineStyle(
                f"Valid rule line styles are {friendly_list(_VALID_LINE_STYLES)}"
            )
        return style

    @classmethod
    def horizontal(
        cls,
        line_style: LineStyle = "solid",
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> Rule:
        return Rule(
            orientation="horizontal",
            line_style=line_style,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )

    @classmethod
    def vertical(
        cls,
        line_style: LineStyle = "solid",
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> Rule:
        return Rule(
            orientation="vertical",
            line_style=line_style,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )
