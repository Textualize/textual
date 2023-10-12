from __future__ import annotations

from time import time
from typing import Awaitable

from rich.console import RenderableType
from rich.style import Style
from rich.text import Text

from ..color import Gradient
from ..css.query import NoMatches
from ..events import Mount
from ..widget import AwaitMount, Widget


class LoadingIndicator(Widget):
    """Display an animated loading indicator."""

    DEFAULT_CSS = """
    LoadingIndicator {
        width: 100%;
        height: 100%;
        min-height: 1;
        content-align: center middle;
        color: $accent;
    }
    LoadingIndicator.-overlay {
        overlay: screen;
        background: $boost;
    }
    """

    def apply(self, widget: Widget) -> AwaitMount:
        """Apply the loading indicator to a `widget`.

        This will overlay the given widget with a loading indicator.

        Args:
            widget: A widget.

        Returns:
            AwaitMount: An awaitable for mounting the indicator.
        """
        self.add_class("-overlay")
        await_mount = widget.mount(self, before=0)
        return await_mount

    @classmethod
    def clear(cls, widget: Widget) -> Awaitable:
        """Clear any loading indicator from the given widget.

        Args:
            widget: Widget to clear the loading indicator from.

        Returns:
            Optional awaitable.
        """
        try:
            await_remove = widget.get_child_by_type(cls).remove()
        except NoMatches:

            async def null() -> None:
                """Nothing to remove"""
                return None

            return null()

        return await_remove

    def _on_mount(self, _: Mount) -> None:
        self._start_time = time()
        self.auto_refresh = 1 / 16

    def render(self) -> RenderableType:
        elapsed = time() - self._start_time
        speed = 0.8
        dot = "\u25cf"
        _, _, background, color = self.colors

        gradient = Gradient(
            (0.0, background.blend(color, 0.1)),
            (0.7, color),
            (1.0, color.lighten(0.1)),
        )

        blends = [(elapsed * speed - dot_number / 8) % 1 for dot_number in range(5)]

        dots = [
            (
                f"{dot} ",
                Style.from_color(gradient.get_color((1 - blend) ** 2).rich_color),
            )
            for blend in blends
        ]
        indicator = Text.assemble(*dots)
        indicator.rstrip()
        return indicator
