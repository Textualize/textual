from __future__ import annotations

from rich.style import Style as RichStyle

from textual.color import Color
from textual.content import Style
from textual.css.styles import RulesMap
from textual.selection import Selection
from textual.strip import Strip
from textual.visual import Visual


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
        self,
        rules: RulesMap,
        width: int,
        height: int | None,
        style: Style,
        selection: Selection | None = None,
        selection_style: Style | None = None,
        post_style: Style | None = None,
    ) -> list[Strip]:
        line_count = 1 if height is None else height
        return [Strip.blank(width, self._rich_style)] * line_count
