from typing import TYPE_CHECKING

from rich.measure import Measurement
from rich.segment import Segment

if TYPE_CHECKING:
    from rich.console import Console, ConsoleOptions, RenderableType, RenderResult
    from rich.style import StyleType


class Styled:
    """A renderable which allows you to apply a style before and after another renderable.
    This can be used to layer styles on top of each other, like a style sandwich. This is used,
    for example, in the DataTable to layer default CSS styles + user renderables (e.g. Text objects
    stored in the cells of the table) + CSS component styles on top of each other."""

    def __init__(
        self,
        renderable: "RenderableType",
        pre_style: "StyleType",
        post_style: "StyleType",
    ) -> None:
        """Construct a Styled.

        Args:
            renderable (RenderableType): Any renderable.
            pre_style (StyleType): A style to apply across the entire renderable.
                Will be applied before the styles from the renderable itself.
            post_style (StyleType): A style to apply across the entire renderable.
                Will be applied after the styles from the renderable itself.
        """
        self.renderable = renderable
        self.pre_style = pre_style
        self.post_style = post_style

    def __rich_console__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> "RenderResult":
        pre_style = console.get_style(self.pre_style)
        post_style = console.get_style(self.post_style)
        rendered_segments = console.render(self.renderable, options)
        segments = Segment.apply_style(
            rendered_segments, style=pre_style, post_style=post_style
        )
        return segments

    def __rich_measure__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> Measurement:
        return Measurement.get(console, options, self.renderable)
