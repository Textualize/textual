"""
Auxiliary widget that renders a bar, used in other widgets like tabs and progress bar.
"""
from __future__ import annotations

from rich.style import Style

from ..app import RenderResult
from ..reactive import reactive
from ..renderables.bar import RenderableBar
from ..widget import Widget


class Bar(Widget):
    """A widget that renders a highlighted bar."""

    DEFAULT_CSS = """
    Bar {
        width: 1fr;
        height: 1;
    }
    Bar > .bar--bar {
        background: $foreground 10%;
    """

    COMPONENT_CLASSES = {"bar--bar"}
    """
    | Class | Description |
    | :- | :- |
    | `bar--bar` | Style of the bar (may be used to change the color). |
    """

    highlight_start = reactive(0)
    """First cell in highlight."""
    highlight_end = reactive(0)
    """Last cell (inclusive) in highlight."""

    @property
    def _highlight_range(self) -> tuple[int, int]:
        """Highlighted range for the bar."""
        return (self.highlight_start, self.highlight_end)

    def render(self) -> RenderResult:
        """Render the bar."""
        bar_style = self.get_component_rich_style("bar--bar")
        return RenderableBar(
            highlight_range=self._highlight_range,
            highlight_style=Style.from_color(bar_style.color),
            background_style=Style.from_color(bar_style.bgcolor),
        )
