from __future__ import annotations

from abc import ABC, abstractmethod
from typing import ClassVar, NamedTuple, TYPE_CHECKING

from .geometry import Region, Size, Spacing
from ._typing import TypeAlias

if TYPE_CHECKING:
    from .widget import Widget

ArrangeResult: TypeAlias = "tuple[list[WidgetPlacement], set[Widget]]"
DockArrangeResult: TypeAlias = "tuple[list[WidgetPlacement], set[Widget], Spacing]"


class WidgetPlacement(NamedTuple):
    """The position, size, and relative order of a widget within its parent."""

    region: Region
    margin: Spacing
    widget: Widget
    order: int = 0
    fixed: bool = False


class Layout(ABC):
    """Responsible for arranging Widgets in a view and rendering them."""

    name: ClassVar[str] = ""

    def __repr__(self) -> str:
        return f"<{self.name}>"

    @abstractmethod
    def arrange(
        self, parent: Widget, children: list[Widget], size: Size
    ) -> ArrangeResult:
        """Generate a layout map that defines where on the screen the widgets will be drawn.

        Args:
            parent (Widget): Parent widget.
            size (Size): Size of container.

        Returns:
            Iterable[WidgetPlacement]: An iterable of widget location
        """

    def get_content_width(self, widget: Widget, container: Size, viewport: Size) -> int:
        """Get the width of the content.

        Args:
            widget (Widget): The container widget.
            container (Size): The container size.
            viewport (Size): The viewport size.

        Returns:
            int: Width of the content.
        """
        width: int | None = None
        gutter_width = widget.gutter.width
        for child in widget.displayed_children:
            if not child.is_container:
                child_width = (
                    child.get_content_width(container, viewport)
                    + gutter_width
                    + child.gutter.width
                )
                width = child_width if width is None else max(width, child_width)
        if width is None:
            width = container.width

        return width

    def get_content_height(
        self, widget: Widget, container: Size, viewport: Size, width: int
    ) -> int:
        """Get the content height.

        Args:
            widget (Widget): The container widget.
            container (Size): The container size.
            viewport (Size): The viewport.
            width (int): The content width.

        Returns:
            int: Content height (in lines).
        """
        if not widget.displayed_children:
            height = container.height
        else:
            placements, *_ = widget._arrange(Size(width, container.height))
            height = max(
                placement.region.bottom + placement.margin.bottom
                for placement in placements
            )
        return height
