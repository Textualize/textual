from __future__ import annotations

from rich.console import RenderableType


from .geometry import Size
from .widget import Widget


class ScrollView(Widget):
    """
    A base class for a Widget that handles it's own scrolling (i.e. doesn't rely
    on the compositor to render children).

    """

    CSS = """
    
    ScrollView {     
        overflow-y: auto;
        overflow-x: auto;        
    }    

    """

    def __init__(
        self, name: str | None = None, id: str | None = None, classes: str | None = None
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)

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

    def size_updated(
        self, size: Size, virtual_size: Size, container_size: Size
    ) -> None:
        """Called when size is updated.

        Args:
            size (Size): New size.
            virtual_size (Size): New virtual size.
            container_size (Size): New container size.
        """
        virtual_size = self.virtual_size
        if self._size != size:
            self._size = size
            self._container_size = container_size

            self._refresh_scrollbars()
            width, height = self.container_size
            if self.show_vertical_scrollbar:
                self.vertical_scrollbar.window_virtual_size = virtual_size.height
                self.vertical_scrollbar.window_size = height
            if self.show_horizontal_scrollbar:
                self.horizontal_scrollbar.window_virtual_size = virtual_size.width
                self.horizontal_scrollbar.window_size = width

            self.scroll_x = self.validate_scroll_x(self.scroll_x)
            self.scroll_y = self.validate_scroll_y(self.scroll_y)
            self.refresh(layout=False)
            self.call_later(self.scroll_to, self.scroll_x, self.scroll_y)

    def render(self) -> RenderableType:
        """Render the scrollable region (if `render_lines` is not implemented).

        Returns:
            RenderableType: Renderable object.
        """
        from rich.panel import Panel

        return Panel(f"{self.scroll_offset} {self.show_vertical_scrollbar}")

    def watch_scroll_x(self, new_value: float) -> None:
        """Called when horizontal bar is scrolled."""
        self.horizontal_scrollbar.position = int(new_value)
        self.refresh(layout=False)

    def watch_scroll_y(self, new_value: float) -> None:
        """Called when vertical bar is scrolled."""
        self.vertical_scrollbar.position = int(new_value)
        self.refresh(layout=False)
