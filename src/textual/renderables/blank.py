from __future__ import annotations

from rich.style import Style as RichStyle

from textual.color import Color
from textual.content import Style
from textual.css.styles import RulesMap
from textual.strip import Strip
from textual.visual import RenderOptions, Visual


class Blank(Visual):
    """Draw solid background color."""

    def __init__(self, color: Color | str = "transparent") -> None:
        self._rich_style = RichStyle.from_color(bgcolor=Color.parse(color).rich_color)

    def visualize(self) -> Blank:
        return self

    def get_optimal_width(self, rules: RulesMap, container_width: int) -> int:
        return container_width

    def get_height(self, rules: RulesMap, width: int) -> int:
        return 1

    def render_strips(
        self, width: int, height: int | None, style: Style, options: RenderOptions
    ) -> list[Strip]:
        """Render the Visual into an iterable of strips. Part of the Visual protocol.

        Args:
            width: Width of desired render.
            height: Height of desired render or `None` for any height.
            style: The base style to render on top of.
            options: Additional render options.

        Returns:
            An list of Strips.
        """
        line_count = 1 if height is None else height
        return [Strip.blank(width, self._rich_style)] * line_count
