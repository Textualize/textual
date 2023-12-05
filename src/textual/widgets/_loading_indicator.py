from __future__ import annotations

from time import time
from typing import Awaitable, ClassVar
from weakref import WeakKeyDictionary

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
        dock: top;
        layer: _loading;
        background: $boost;
    }
    """

    _widget_state: ClassVar[
        WeakKeyDictionary[Widget, tuple[bool, str, str, str]]
    ] = WeakKeyDictionary()
    """Widget state that must be restore after loading.

    The tuples indicate the original values of the:
     - widget disabled state;
     - widget style overflow_x rule;
     - widget style overflow_y rule; and
     - widget style scrollbar_gutter rule.
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

    def apply(self, widget: Widget) -> AwaitMount:
        """Apply the loading indicator to a `widget`.

        This will overlay the given widget with a loading indicator.

        Args:
            widget: A widget.

        Returns:
            An awaitable for mounting the indicator.
        """
        self.add_class("-overlay")
        await_mount = widget.mount(self)
        self._widget_state[widget] = (
            widget.disabled,
            widget.styles.overflow_x,
            widget.styles.overflow_y,
            widget.styles.scrollbar_gutter,
        )
        widget.styles.scrollbar_gutter = "auto"
        widget.styles.overflow_x = "hidden"
        widget.styles.overflow_y = "hidden"
        widget.disabled = True
        return await_mount

    @classmethod
    def clear(cls, widget: Widget) -> Awaitable[None]:
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

            await_remove = null()

        if widget in cls._widget_state:
            disabled, overflow_x, overflow_y, scrollbar_gutter = cls._widget_state[
                widget
            ]
            widget.styles.scrollbar_gutter = scrollbar_gutter
            widget.styles.overflow_x = overflow_x
            widget.styles.overflow_y = overflow_y
            widget.disabled = disabled

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
