from __future__ import annotations

from rich.console import RenderableType

from .geometry import Size
from .widget import Widget


class ScrollView(Widget):
    """
    A base class for a Widget that handles it's own scrolling (i.e. doesn't rely
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

    @property
    def is_transparent(self) -> bool:
        """Not transparent, i.e. renders something."""
        return False

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
