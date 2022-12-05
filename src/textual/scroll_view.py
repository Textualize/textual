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

    def on_mount(self):
        self._refresh_scrollbars()

    def get_content_width(self, container: Size, viewport: Size) -> int:
        """Gets the width of the content area.

        Args:
            container (Size): Size of the container (immediate parent) widget.
            viewport (Size): Size of the viewport.

        Returns:
            int: The optimal width of the content.
        """
        return self.virtual_size.width

    def get_content_height(self, container: Size, viewport: Size, width: int) -> int:
        """Gets the height (number of lines) in the content area.

        Args:
            container (Size): Size of the container (immediate parent) widget.
            viewport (Size): Size of the viewport.
            width (int): Width of renderable.

        Returns:
            int: The height of the content.
        """
        return self.virtual_size.height

    def _size_updated(
        self, size: Size, virtual_size: Size, container_size: Size
    ) -> None:
        """Called when size is updated.

        Args:
            size (Size): New size.
            virtual_size (Size): New virtual size.
            container_size (Size): New container size.
        """
        if (
            self._size != size
            or virtual_size != self.virtual_size
            or container_size != self.container_size
        ):
            self._size = size
            virtual_size = self.virtual_size
            self._container_size = size - self.styles.gutter.totals
            self._scroll_update(virtual_size)

            self.scroll_to(self.scroll_x, self.scroll_y, animate=False)
            self.refresh()

    def render(self) -> RenderableType:
        """Render the scrollable region (if `render_lines` is not implemented).

        Returns:
            RenderableType: Renderable object.
        """
        from rich.panel import Panel

        return Panel(f"{self.scroll_offset} {self.show_vertical_scrollbar}")
