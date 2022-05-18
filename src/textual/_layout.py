from __future__ import annotations

from abc import ABC, abstractmethod
import sys
from typing import ClassVar, NamedTuple, TYPE_CHECKING


from .geometry import Region, Offset, Size

if sys.version_info >= (3, 10):
    from typing import TypeAlias
else:  # pragma: no cover
    from typing_extensions import TypeAlias


if TYPE_CHECKING:
    from .widget import Widget

ArrangeResult: TypeAlias = "tuple[list[WidgetPlacement], set[Widget]]"


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
    def arrange(self, parent: Widget, size: Size) -> ArrangeResult:
        """Generate a layout map that defines where on the screen the widgets will be drawn.

        Args:
            parent (Widget): Parent widget.
            size (Size): Size of container.

        Returns:
            Iterable[WidgetPlacement]: An iterable of widget location
        """

    def get_content_width(self, widget: Widget, container: Size, viewport: Size) -> int:
        width: int | None = None
        for child in widget.displayed_children:
            assert isinstance(child, Widget)
            if not child.is_container:
                child_width = child.get_content_width(container, viewport)
                width = child_width if width is None else max(width, child_width)
        if width is None:
            width = container.width
        return width

    def get_content_height(
        self, widget: Widget, container: Size, viewport: Size, width: int
    ) -> int:
        if not widget.displayed_children:
            height = container.height
        else:
            placements, widgets = self.arrange(widget, Size(width, container.height))
            height = max(placement.region.y_max for placement in placements)
        return height
