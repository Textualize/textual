from __future__ import annotations

from typing import Callable, ClassVar, Sequence

from textual.app import RenderResult

from ..reactive import reactive
from ..renderables.sparkline import SparklineRenderable
from ..widget import Widget


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
    | `sparkline--min-color` | The colour used for the smaller values in the data. |
    """

    DEFAULT_CSS = """
    Sparkline > .sparkline--max-color {
        color: $error;
    }
    Sparkline > .sparkline--min-color {
        color: $success;
    }
    """

    data: reactive[Sequence[int | float] | None]
    """The data that populates the sparkline."""
    width: reactive[int | None]
    """The width of the sparkline/number of buckets to partition data into."""
    summary_function: reactive[Callable[[Sequence[int | float]], float]]
    """The function that computes the value that represents each bucket."""

    def __init__(
        self,
        data: Sequence[int | float] | None = None,
        *,
        summary_function: Callable[[Sequence[int | float]], float] = max,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        """Initialize a sparkline widget.

        Args:
            data: The initial data to populate the sparkline with.
            summary_function: Summarises bucket values into a single value used to
                represent each bucket.
            name: The name of the widget.
            id: The ID of the widget in the DOM.
            classes: The CSS classes for the widget.
            disabled: Whether the widget is disabled or not.
        """
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self.data = data
        self.summary_function = summary_function

    def render(self) -> RenderResult:
        """Renders the sparkline when there is data available."""
        if not self.data:
            return "<empty sparkline>"
        return SparklineRenderable(
            self.data,
            width=None,
            min_color=self.get_component_styles(
                "sparkline--min-color"
            ).color.rich_color,
            max_color=self.get_component_styles(
                "sparkline--max-color"
            ).color.rich_color,
            summary_function=self.summary_function,
        )
