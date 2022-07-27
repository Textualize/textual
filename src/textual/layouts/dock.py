from __future__ import annotations

import sys
from collections import defaultdict
from dataclasses import dataclass
from operator import attrgetter
from typing import TYPE_CHECKING, NamedTuple, Sequence

from .._layout_resolve import layout_resolve
from ..css.types import Edge
from ..geometry import Region, Size
from .._layout import ArrangeResult, Layout, WidgetPlacement
from ..widget import Widget

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal

if TYPE_CHECKING:
    from ..screen import Screen

DockEdge = Literal["top", "right", "bottom", "left"]


@dataclass
class DockOptions:
    size: int | None = None
    fraction: int | None = 1
    min_size: int = 1

    def __post_init__(self) -> None:
        if self.size is None and self.fraction is None:
            self.fraction = 1


class Dock(NamedTuple):
    edge: Edge
    widgets: Sequence[Widget]
    z: int = 0


class DockLayout(Layout):
    """Dock Widgets to edge of screen."""

    name = "dock"

    def __init__(self) -> None:
        super().__init__()
        self._docks: list[Dock] | None = None

    def __repr__(self):
        return "<DockLayout>"

    def get_docks(self, parent: Widget, children: list[Widget]) -> list[Dock]:
        groups: dict[str, list[Widget]] = defaultdict(list)
        for child in children:
            assert isinstance(child, Widget)
            groups[child.styles.dock].append(child)
        docks: list[Dock] = []
        append_dock = docks.append
        for name, edge, z in parent.styles.docks:
            append_dock(Dock(edge, groups[name], z))
        return docks

    def arrange(
        self, parent: Widget, children: list[Widget], size: Size
    ) -> ArrangeResult:

        width, height = size
        layout_region = Region(0, 0, width, height)
        layers: dict[int, Region] = defaultdict(lambda: layout_region)

        docks = self.get_docks(parent, children)

        def make_dock_options(widget: Widget, edge: Edge) -> DockOptions:
            styles = widget.styles
            has_rule = styles.has_rule

            # TODO: This was written pre resolve_dimension, we should update this to use available units
            return (
                DockOptions(
                    styles.width.cells if has_rule("width") else None,
                    styles.width.fraction if has_rule("width") else 1,
                    styles.min_width.cells if has_rule("min_width") else 1,
                )
                if edge in ("left", "right")
                else DockOptions(
                    styles.height.cells if has_rule("height") else None,
                    styles.height.fraction if has_rule("height") else 1,
                    styles.min_height.cells if has_rule("min_height") else 1,
                )
            )

        placements: list[WidgetPlacement] = []
        add_placement = placements.append
        arranged_widgets: set[Widget] = set()

        for z, (edge, widgets, _z) in enumerate(sorted(docks, key=attrgetter("z"))):

            arranged_widgets.update(widgets)
            dock_options = [make_dock_options(widget, edge) for widget in widgets]
            region = layers[z]
            if not region.area:
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
                    add_placement(
                        WidgetPlacement(Region(x, render_y, width, new_size), widget, z)
                    )
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
                    add_placement(
                        WidgetPlacement(
                            Region(x, render_y - new_size, width, new_size), widget, z
                        )
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
                    add_placement(
                        WidgetPlacement(
                            Region(render_x, y, new_size, height), widget, z
                        )
                    )
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
                    add_placement(
                        WidgetPlacement(
                            Region(render_x - new_size, y, new_size, height), widget, z
                        )
                    )
                    render_x -= new_size
                    remaining = max(0, remaining - new_size)
                region = Region(x, y, width - total, height)

            layers[z] = region

        return ArrangeResult(placements, arranged_widgets)
