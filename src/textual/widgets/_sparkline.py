from __future__ import annotations

from typing import Callable, ClassVar, Optional, Sequence

from textual.app import RenderResult
from textual.color import Color
from textual.reactive import reactive
from textual.renderables.sparkline import Sparkline as SparklineRenderable
from textual.widget import Widget


def _max_factory() -> Callable[[Sequence[float]], float]:
    """Callable that returns the built-in max to initialise a reactive."""
    return max


class Sparkline(Widget):
    """A sparkline widget to display numerical data."""

    COMPONENT_CLASSES: ClassVar[set[str]] = {
        "sparkline--max-color",
        "sparkline--min-color",
    }
    """
    Use these component classes to define the two colors that the sparkline
    interpolates to represent its numerical data.

    Note:
        These two component classes are used exclusively for the _color_ of the
        sparkline widget. Setting any style other than [`color`](/styles/color.md)
        will have no effect.

    | Class | Description |
    | :- | :- |
    | `sparkline--max-color` | The color used for the larger values in the data. |
    | `sparkline--min-color` | The color used for the smaller values in the data. |
    """

    DEFAULT_CSS = """
    Sparkline {
        height: 1;
    }
    Sparkline > .sparkline--max-color {
        color: $accent;
    }
    Sparkline > .sparkline--min-color {
        color: $accent 30%;
    }
    """

    data = reactive[Optional[Sequence[float]]](None)
    """The data that populates the sparkline."""
    summary_function = reactive[Callable[[Sequence[float]], float]](_max_factory)
    """The function that computes the value that represents each bar."""

    def __init__(
        self,
        data: Sequence[float] | None = None,
        *,
        min_color: Color | str | None = None,
        max_color: Color | str | None = None,
        summary_function: Callable[[Sequence[float]], float] | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        """Initialize a sparkline widget.

        Args:
            data: The initial data to populate the sparkline with.
            min_color: The color of the minimum value, or `None` to take from CSS.
            max_color: the color of the maximum value, or `None` to take from CSS.
            summary_function: Summarizes bar values into a single value used to
                represent each bar.
            name: The name of the widget.
            id: The ID of the widget in the DOM.
            classes: The CSS classes for the widget.
            disabled: Whether the widget is disabled or not.
        """
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self.min_color = None if min_color is None else Color.parse(min_color)
        self.max_color = None if max_color is None else Color.parse(max_color)
        self.data = data
        if summary_function is not None:
            self.summary_function = summary_function

    def render(self) -> RenderResult:
        """Renders the sparkline when there is data available."""
        if not self.data:
            return "<empty sparkline>"
        _, base = self.background_colors
        min_color = base + (
            self.get_component_styles("sparkline--min-color").color
            if self.min_color is None
            else self.min_color
        )
        max_color = base + (
            self.get_component_styles("sparkline--max-color").color
            if self.max_color is None
            else self.max_color
        )
        return SparklineRenderable(
            self.data,
            width=self.size.width,
            min_color=min_color.rich_color,
            max_color=max_color.rich_color,
            summary_function=self.summary_function,
        )
