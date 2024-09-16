from __future__ import annotations

from typing import Iterable

from rich.console import Console, ConsoleOptions
from rich.segment import Segment
from rich.style import Style
from typing_extensions import Literal

from textual.app import RenderResult
from textual.css._error_tools import friendly_list
from textual.geometry import Size
from textual.reactive import Reactive, reactive
from textual.widget import Widget

RuleOrientation = Literal["horizontal", "vertical"]
"""The valid orientations of the rule widget."""

LineStyle = Literal[
    "ascii",
    "blank",
    "dashed",
    "double",
    "heavy",
    "hidden",
    "none",
    "solid",
    "thick",
]
"""The valid line styles of the rule widget."""


_VALID_RULE_ORIENTATIONS = {"horizontal", "vertical"}

_VALID_LINE_STYLES = {
    "ascii",
    "blank",
    "dashed",
    "double",
    "heavy",
    "hidden",
    "none",
    "solid",
    "thick",
}

_HORIZONTAL_LINE_CHARS: dict[LineStyle, str] = {
    "ascii": "-",
    "blank": " ",
    "dashed": "╍",
    "double": "═",
    "heavy": "━",
    "hidden": " ",
    "none": " ",
    "solid": "─",
    "thick": "█",
}

_VERTICAL_LINE_CHARS: dict[LineStyle, str] = {
    "ascii": "|",
    "blank": " ",
    "dashed": "╏",
    "double": "║",
    "heavy": "┃",
    "hidden": " ",
    "none": " ",
    "solid": "│",
    "thick": "█",
}


class InvalidRuleOrientation(Exception):
    """Exception raised for an invalid rule orientation."""


class InvalidLineStyle(Exception):
    """Exception raised for an invalid rule line style."""


class HorizontalRuleRenderable:
    """Renders a horizontal rule."""

    def __init__(self, character: str, style: Style, width: int):
        self.character = character
        self.style = style
        self.width = width

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> Iterable[Segment]:
        yield Segment(self.width * self.character, self.style)


class VerticalRuleRenderable:
    """Renders a vertical rule."""

    def __init__(self, character: str, style: Style, height: int):
        self.character = character
        self.style = style
        self.height = height

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> Iterable[Segment]:
        segment = Segment(self.character, self.style)
        new_line = Segment.line()
        return ([segment, new_line] * self.height)[:-1]


class Rule(Widget, can_focus=False):
    """A rule widget to separate content, similar to a `<hr>` HTML tag."""

    DEFAULT_CSS = """
    Rule {
        color: $primary;
    }

    Rule.-horizontal {
        height: 1;
        margin: 1 0;
        width: 1fr;      
    }

    Rule.-vertical {
        width: 1;
        margin: 0 2;
        height: 1fr;
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
        self.expand = True

    def render(self) -> RenderResult:
        rule_character: str
        style = self.rich_style
        if self.orientation == "vertical":
            rule_character = _VERTICAL_LINE_CHARS[self.line_style]
            return VerticalRuleRenderable(
                rule_character, style, self.content_size.height
            )
        elif self.orientation == "horizontal":
            rule_character = _HORIZONTAL_LINE_CHARS[self.line_style]
            return HorizontalRuleRenderable(
                rule_character, style, self.content_size.width
            )
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

    def get_content_width(self, container: Size, viewport: Size) -> int:
        if self.orientation == "horizontal":
            return container.width
        return 1

    def get_content_height(self, container: Size, viewport: Size, width: int) -> int:
        if self.orientation == "horizontal":
            return 1
        return container.height

    @classmethod
    def horizontal(
        cls,
        line_style: LineStyle = "solid",
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> Rule:
        """Utility constructor for creating a horizontal rule.

        Args:
            line_style: The line style of the rule.
            name: The name of the widget.
            id: The ID of the widget in the DOM.
            classes: The CSS classes of the widget.
            disabled: Whether the widget is disabled or not.

        Returns:
            A rule widget with horizontal orientation.
        """
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
        """Utility constructor for creating a vertical rule.

        Args:
            line_style: The line style of the rule.
            name: The name of the widget.
            id: The ID of the widget in the DOM.
            classes: The CSS classes of the widget.
            disabled: Whether the widget is disabled or not.

        Returns:
            A rule widget with vertical orientation.
        """
        return Rule(
            orientation="vertical",
            line_style=line_style,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )
