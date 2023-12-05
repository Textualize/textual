"""
`ScrollView` is a base class for [line api](/guide/widgets#line-api) widgets.
"""

from __future__ import annotations

from rich.console import RenderableType

from ._animator import EasingFunction
from ._types import CallbackType
from .containers import ScrollableContainer
from .geometry import Region, Size


class ScrollView(ScrollableContainer):
    """
    A base class for a Widget that handles its own scrolling (i.e. doesn't rely
    on the compositor to render children).
    """

    DEFAULT_CSS = """
    ScrollView {
        overflow-y: auto;
        overflow-x: auto;
    }
    """

    @property
    def is_scrollable(self) -> bool:
        """Always scrollable."""
        return True

    def watch_scroll_x(self, old_value: float, new_value: float) -> None:
        if self.show_horizontal_scrollbar and round(old_value) != round(new_value):
            self.horizontal_scrollbar.position = round(new_value)
            self.refresh()

    def watch_scroll_y(self, old_value: float, new_value: float) -> None:
        if self.show_vertical_scrollbar and round(old_value) != round(new_value):
            self.vertical_scrollbar.position = round(new_value)
            self.refresh()

    def on_mount(self):
        self._refresh_scrollbars()

    def get_content_width(self, container: Size, viewport: Size) -> int:
        """Gets the width of the content area.

        Args:
            container: Size of the container (immediate parent) widget.
            viewport: Size of the viewport.

        Returns:
            The optimal width of the content.
        """
        return self.virtual_size.width

    def get_content_height(self, container: Size, viewport: Size, width: int) -> int:
        """Gets the height (number of lines) in the content area.

        Args:
            container: Size of the container (immediate parent) widget.
            viewport: Size of the viewport.
            width: Width of renderable.

        Returns:
            The height of the content.
        """
        return self.virtual_size.height

    def _size_updated(
        self, size: Size, virtual_size: Size, container_size: Size, layout: bool = True
    ) -> bool:
        """Called when size is updated.

        Args:
            size: New size.
            virtual_size: New virtual size.
            container_size: New container size.
            layout: Perform layout if required.

        Returns:
            True if anything changed, or False if nothing changed.
        """
        if self._size != size or self._container_size != container_size:
            self.refresh()
        if (
            self._size != size
            or virtual_size != self.virtual_size
            or container_size != self.container_size
        ):
            self._size = size
            virtual_size = self.virtual_size
            self._container_size = size - self.styles.gutter.totals
            self._scroll_update(virtual_size)
            return True
        else:
            return False

    def render(self) -> RenderableType:
        """Render the scrollable region (if `render_lines` is not implemented).

        Returns:
            Renderable object.
        """
        from rich.panel import Panel

        return Panel(f"{self.scroll_offset} {self.show_vertical_scrollbar}")

    # Custom scroll to which doesn't require call_after_refresh
    def scroll_to(
        self,
        x: float | None = None,
        y: float | None = None,
        *,
        animate: bool = True,
        speed: float | None = None,
        duration: float | None = None,
        easing: EasingFunction | str | None = None,
        force: bool = False,
        on_complete: CallbackType | None = None,
    ) -> None:
        """Scroll to a given (absolute) coordinate, optionally animating.

        Args:
            x: X coordinate (column) to scroll to, or `None` for no change.
            y: Y coordinate (row) to scroll to, or `None` for no change.
            animate: Animate to new scroll position.
            speed: Speed of scroll if `animate` is `True`; or `None` to use `duration`.
            duration: Duration of animation, if `animate` is `True` and `speed` is `None`.
            easing: An easing method for the scrolling animation.
            force: Force scrolling even when prohibited by overflow styling.
            on_complete: A callable to invoke when the animation is finished.
        """

        self._scroll_to(
            x,
            y,
            animate=animate,
            speed=speed,
            duration=duration,
            easing=easing,
            force=force,
            on_complete=on_complete,
        )

    def refresh_lines(self, y_start: int, line_count: int = 1) -> None:
        """Refresh one or more lines.

        Args:
            y_start: First line to refresh.
            line_count: Total number of lines to refresh.
        """

        width = self.size.width
        scroll_x, scroll_y = self.scroll_offset
        refresh_region = Region(scroll_x, y_start - scroll_y, width, line_count)
        self.refresh(refresh_region)
