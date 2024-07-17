from __future__ import annotations

from typing import NamedTuple

from textual.geometry import Region, Size, Spacing


class MapGeometry(NamedTuple):
    """Defines the absolute location of a Widget."""

    region: Region
    """The (screen) [region][textual.geometry.Region] occupied by the widget."""
    order: tuple[tuple[int, int, int], ...]
    """Tuple of tuples defining the painting order of the widget.

    Each successive triple represents painting order information with regards to
    ancestors in the DOM hierarchy and the last triple provides painting order
    information for this specific widget.
    """
    clip: Region
    """A [region][textual.geometry.Region] to clip the widget by (if a Widget is within a container)."""
    virtual_size: Size
    """The virtual [size][textual.geometry.Size] (scrollable area) of a widget if it is a container."""
    container_size: Size
    """The container [size][textual.geometry.Size] (area not occupied by scrollbars)."""
    virtual_region: Region
    """The [region][textual.geometry.Region] relative to the container (but not necessarily visible)."""
    dock_gutter: Spacing
    """Space from the container reserved by docked widgets."""

    @property
    def visible_region(self) -> Region:
        """The Widget region after clipping."""
        return self.clip.intersection(self.region)
