from __future__ import annotations

from time import time
from typing import TYPE_CHECKING

from rich.style import Style
from rich.text import Text

if TYPE_CHECKING:
    from textual.app import RenderResult
from textual.color import Gradient
from textual.events import Mount
from textual.widget import Widget


class LoadingIndicator(Widget):
    """Display an animated loading indicator."""

    DEFAULT_CSS = """
    LoadingIndicator {
        width: 100%;
        height: 100%;
        min-height: 1;
        content-align: center middle;
        color: $accent;
        text-style: not reverse;
    }
    LoadingIndicator.-textual-loading-indicator {
        layer: _loading;
        background: $boost;
        dock: top;
    }
    """

    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ):
        """Initialize a loading indicator.

        Args:
            name: The name of the widget.
            id: The ID of the widget in the DOM.
            classes: The CSS classes for the widget.
            disabled: Whether the widget is disabled or not.
        """
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)

        self._start_time: float = 0.0
        """The time the loading indicator was mounted (a Unix timestamp)."""

    def _on_mount(self, _: Mount) -> None:
        self._start_time = time()
        self.auto_refresh = 1 / 16

    def render(self) -> RenderResult:
        if self.app.animation_level == "none":
            return Text("Loading...")

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
