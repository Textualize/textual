from __future__ import annotations

import sys
from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable, TYPE_CHECKING, Sequence

from ..app import active_app

from ..dom import DOMNode
from .._layout_resolve import layout_resolve
from ..geometry import Offset, Region, Size
from ..layout import Layout, WidgetPlacement
from ..layout_map import LayoutMap
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


@dataclass
class Dock:
    edge: str
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
            groups[child.styles.dock_group].append(child)
        docks: list[Dock] = []
        append_dock = docks.append
        for name, edge in view.styles.docks:
            append_dock(Dock(edge, groups[name], 0))
        return docks

    def get_widgets(self, view: View) -> Iterable[DOMNode]:
        for dock in self.get_docks(view):
            yield from dock.widgets

    def arrange(
        self, view: View, size: Size, scroll: Offset
    ) -> Iterable[WidgetPlacement]:

        map: LayoutMap = LayoutMap(size)
        width, height = size
        layout_region = Region(0, 0, width, height)
        layers: dict[int, Region] = defaultdict(lambda: layout_region)

        docks = self.get_docks(view)

        for index, dock in enumerate(docks):

            dock_options = [
                (
                    DockOptions(
                        widget.styles.width.cells,
                        widget.styles.width.fraction or 1,
                        widget.styles.min_width.cells or 1,
                    )
                    if dock.edge in ("left", "right")
                    else DockOptions(
                        widget.styles.height.cells,
                        widget.styles.height.fraction or 1,
                        widget.styles.min_height.cells or 1,
                    )
                )
                for widget in dock.widgets
            ]
            region = layers[dock.z]
            if not region:
                # No space left
                continue

            order = (dock.z, index)
            x, y, width, height = region

            if dock.edge == "top":
                sizes = layout_resolve(height, dock_options)
                render_y = y
                remaining = region.height
                total = 0
                for widget, layout_size in zip(dock.widgets, sizes):
                    if not widget.visible:
                        continue
                    layout_size = min(remaining, layout_size)
                    if not layout_size:
                        break
                    total += layout_size
                    yield WidgetPlacement(
                        Region(x, render_y, width, layout_size), widget, order
                    )
                    render_y += layout_size
                    remaining = max(0, remaining - layout_size)
                region = Region(x, y + total, width, height - total)

            elif dock.edge == "bottom":
                sizes = layout_resolve(height, dock_options)
                render_y = y + height
                remaining = region.height
                total = 0
                for widget, layout_size in zip(dock.widgets, sizes):
                    if not widget.visible:
                        continue
                    layout_size = min(remaining, layout_size)
                    if not layout_size:
                        break
                    total += layout_size
                    yield WidgetPlacement(
                        Region(x, render_y - layout_size, width, layout_size),
                        widget,
                        order,
                    )
                    render_y -= layout_size
                    remaining = max(0, remaining - layout_size)
                region = Region(x, y, width, height - total)

            elif dock.edge == "left":
                sizes = layout_resolve(width, dock_options)
                render_x = x
                remaining = region.width
                total = 0
                for widget, layout_size in zip(dock.widgets, sizes):
                    if not widget.visible:
                        continue
                    layout_size = min(remaining, layout_size)
                    if not layout_size:
                        break
                    total += layout_size
                    yield WidgetPlacement(
                        Region(render_x, y, layout_size, height),
                        widget,
                        order,
                    )
                    render_x += layout_size
                    remaining = max(0, remaining - layout_size)
                region = Region(x + total, y, width - total, height)

            elif dock.edge == "right":
                sizes = layout_resolve(width, dock_options)
                render_x = x + width
                remaining = region.width
                total = 0
                for widget, layout_size in zip(dock.widgets, sizes):
                    if not widget.visible:
                        continue
                    layout_size = min(remaining, layout_size)
                    if not layout_size:
                        break
                    total += layout_size
                    yield WidgetPlacement(
                        Region(render_x - layout_size, y, layout_size, height),
                        widget,
                        order,
                    )
                    render_x -= layout_size
                    remaining = max(0, remaining - layout_size)
                region = Region(x, y, width - total, height)

            layers[dock.z] = region

        return map
