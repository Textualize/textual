from __future__ import annotations

from abc import ABC, abstractmethod
from typing import ClassVar, NamedTuple, TYPE_CHECKING


from .geometry import Region, Offset, Size


if TYPE_CHECKING:
    from .widget import Widget


class WidgetPlacement(NamedTuple):
    """The position, size, and relative order of a widget within its parent."""

    region: Region
    widget: Widget | None = None  # A widget of None means empty space
    order: int = 0


class Layout(ABC):
    """Responsible for arranging Widgets in a view and rendering them."""

    name: ClassVar[str] = ""

    def __repr__(self) -> str:
        return f"<{self.name}>"

    @abstractmethod
    def arrange(
        self, parent: Widget, size: Size, scroll: Offset
    ) -> tuple[list[WidgetPlacement], set[Widget]]:
        """Generate a layout map that defines where on the screen the widgets will be drawn.

        Args:
            parent (Widget): Parent widget.
            size (Size): Size of container.
            scroll (Offset): Offset to apply to the Widget placements.

        Returns:
            Iterable[WidgetPlacement]: An iterable of widget location
        """

    def get_content_width(
        self, parent: Widget, container_size: Size, viewport_size: Size
    ) -> int:
        width: int | None = None
        for child in parent.displayed_children:
            assert isinstance(child, Widget)
            if not child.is_container:
                child_width = child.get_content_width(container_size, viewport_size)
                width = child_width if width is None else max(width, child_width)
        if width is None:
            width = container_size.width
        return width

    def get_content_height(
        self, parent: Widget, container_size: Size, viewport_size: Size, width: int
    ) -> int:
        if not parent.displayed_children:
            height = container_size.height
        else:
            placements, widgets = self.arrange(
                parent, Size(width, container_size.height), Offset(0, 0)
            )
            height = max(placement.region.y_max for placement in placements)
        return height
