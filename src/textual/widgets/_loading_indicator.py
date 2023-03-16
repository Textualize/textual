from __future__ import annotations

from time import time

from rich.console import RenderableType
from rich.style import Style
from rich.text import Text

from ..color import Gradient
from ..widget import Widget


class LoadingIndicator(Widget):
    """Display an animated loading indicator."""

    DEFAULT_CSS = """
    LoadingIndicator {
        width: 100%;
        height: 100%;
        content-align: center middle;
        color: $accent;
    }
    """

    def on_mount(self) -> None:
        self._start_time = time()
        self.auto_refresh = 1 / 16

    def render(self) -> RenderableType:
        elapsed = time() - self._start_time
        speed = 0.8
        dot = "\u25CF"
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
