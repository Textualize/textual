from __future__ import annotations

from abc import ABC, abstractmethod
from typing import ClassVar, Iterable, NamedTuple, TYPE_CHECKING


from .geometry import Region, Offset, Size


if TYPE_CHECKING:
    from .widget import Widget
    from .screen import Screen


class WidgetPlacement(NamedTuple):
    """The position, size, and relative order of a widget within its parent."""

    region: Region
    widget: Widget | None = None  # A widget of None means empty space
    order: int = 0

    def apply_margin(self) -> "WidgetPlacement":
        """Apply any margin present in the styles of the widget by shrinking the
        region appropriately.

        Returns:
            WidgetPlacement: Returns ``self`` if no ``margin`` styles are present in
                the widget. Otherwise, returns a copy of self with a region shrunk to
                account for margin.
        """
        region, widget, order = self
        if widget is not None:
            styles = widget.styles
            if styles.margin:
                return WidgetPlacement(
                    region=region.shrink(styles.margin),
                    widget=widget,
                    order=order,
                )
        return self


class Layout(ABC):
    """Responsible for arranging Widgets in a view and rendering them."""

    name: ClassVar[str] = ""

    @abstractmethod
    def arrange(
        self, parent: Widget, size: Size, scroll: Offset
    ) -> tuple[Iterable[WidgetPlacement], set[Widget]]:
        """Generate a layout map that defines where on the screen the widgets will be drawn.

        Args:
            parent (Widget): Parent widget.
            size (Size): Size of container.
            scroll (Offset): Offset to apply to the Widget placements.

        Returns:
            Iterable[WidgetPlacement]: An iterable of widget location
        """
