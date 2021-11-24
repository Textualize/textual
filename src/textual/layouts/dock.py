from __future__ import annotations

import sys
from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable, TYPE_CHECKING, NamedTuple, Sequence


from .. import log
from ..dom import DOMNode
from .._layout_resolve import layout_resolve
from ..geometry import Offset, Region, Size
from ..layout import Layout, WidgetPlacement
from ..layout_map import LayoutMap
from ..css.types import Edge
from ..widget import Widget

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal


if TYPE_CHECKING:
    from ..widget import Widget
    from ..view import View


DockEdge = Literal["top", "right", "bottom", "left"]


@dataclass
class DockOptions:
    size: int | None = None
    fraction: int = 1
    min_size: int = 1


class Dock(NamedTuple):
    edge: Edge
    widgets: Sequence[Widget]
    z: int = 0


class DockLayout(Layout):
    def __init__(self) -> None:
        super().__init__()
        self._docks: list[Dock] | None = None

    def get_docks(self, view: View) -> list[Dock]:
        groups: dict[str, list[Widget]] = defaultdict(list)
        for child in view.children:
            assert isinstance(child, Widget)
            if child.visible:
                groups[child.styles.dock_group].append(child)
        docks: list[Dock] = []
        append_dock = docks.append
        for name, edge, z in view.styles.docks:
            append_dock(Dock(edge, groups[name], z))
        return docks

    def get_widgets(self, view: View) -> Iterable[DOMNode]:
        for dock in self.get_docks(view):
            yield from dock.widgets

    def arrange(
        self, view: View, size: Size, scroll: Offset
    ) -> Iterable[WidgetPlacement]:

        width, height = size
        layout_region = Region(0, 0, width, height)
        layers: dict[int, Region] = defaultdict(lambda: layout_region)

        docks = self.get_docks(view)

        def make_dock_options(widget, edge: Edge) -> DockOptions:
            styles = widget.styles

            return (
                DockOptions(
                    styles.width.cells if styles._rule_width is not None else None,
                    styles.width.fraction if styles._rule_width is not None else 1,
                    styles.min_width.cells if styles._rule_min_width is not None else 1,
                )
                if edge in ("left", "right")
                else DockOptions(
                    styles.height.cells if styles._rule_height is not None else None,
                    styles.height.fraction if styles._rule_height is not None else 1,
                    styles.min_height.cells
                    if styles._rule_min_height is not None
                    else 1,
                )
            )

        Placement = WidgetPlacement

        for edge, widgets, z in docks:

            dock_options = [make_dock_options(widget, edge) for widget in widgets]
            region = layers[z]
            if not region:
                # No space left
                continue

            x, y, width, height = region

            if edge == "top":
                sizes = layout_resolve(height, dock_options)
                render_y = y
                remaining = region.height
                total = 0
                for widget, new_size in zip(widgets, sizes):
                    new_size = min(remaining, new_size)
                    if not new_size:
                        break
                    total += new_size
                    yield Placement(Region(x, render_y, width, new_size), widget, z)
                    render_y += new_size
                    remaining = max(0, remaining - new_size)
                region = Region(x, y + total, width, height - total)

            elif edge == "bottom":
                sizes = layout_resolve(height, dock_options)
                render_y = y + height
                remaining = region.height
                total = 0
                for widget, new_size in zip(widgets, sizes):
                    new_size = min(remaining, new_size)
                    if not new_size:
                        break
                    total += new_size
                    yield Placement(
                        Region(x, render_y - new_size, width, new_size), widget, z
                    )
                    render_y -= new_size
                    remaining = max(0, remaining - new_size)
                region = Region(x, y, width, height - total)

            elif edge == "left":
                sizes = layout_resolve(width, dock_options)
                render_x = x
                remaining = region.width
                total = 0
                for widget, new_size in zip(widgets, sizes):
                    new_size = min(remaining, new_size)
                    if not new_size:
                        break
                    total += new_size
                    yield Placement(Region(render_x, y, new_size, height), widget, z)
                    render_x += new_size
                    remaining = max(0, remaining - new_size)
                region = Region(x + total, y, width - total, height)

            elif edge == "right":
                sizes = layout_resolve(width, dock_options)
                render_x = x + width
                remaining = region.width
                total = 0
                for widget, new_size in zip(widgets, sizes):
                    new_size = min(remaining, new_size)
                    if not new_size:
                        break
                    total += new_size
                    yield Placement(
                        Region(render_x - new_size, y, new_size, height), widget, z
                    )
                    render_x -= new_size
                    remaining = max(0, remaining - new_size)
                region = Region(x, y, width - total, height)

            layers[z] = region
