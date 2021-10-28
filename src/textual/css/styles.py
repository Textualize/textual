from __future__ import annotations

from dataclasses import dataclass, field

from rich import print
import rich.repr
from rich.style import Style

from .errors import StyleValueError
from ._error_tools import friendly_list
from .constants import (
    VALID_DISPLAY,
    VALID_VISIBILITY,
    VALID_LAYOUT,
    NULL_SPACING,
)
from ..geometry import NULL_OFFSET, Offset, Spacing
from ._style_properties import (
    BorderProperty,
    BoxProperty,
    DockEdgeProperty,
    DocksProperty,
    DockGroupProperty,
    IntegerProperty,
    OffsetProperty,
    NameProperty,
    NameListProperty,
    SpacingProperty,
    StringProperty,
    StyleProperty,
)
from .types import Display, Visibility


@dataclass
class Styles:

    _rule_display: Display | None = None
    _rule_visibility: Visibility | None = None
    _rule_layout: str | None = None

    _rule_text: Style | None = None

    _rule_padding: Spacing | None = None
    _rule_margin: Spacing | None = None
    _rule_offset: Offset | None = None

    _rule_border_top: tuple[str, Style] | None = None
    _rule_border_right: tuple[str, Style] | None = None
    _rule_border_bottom: tuple[str, Style] | None = None
    _rule_border_left: tuple[str, Style] | None = None

    _rule_outline_top: tuple[str, Style] | None = None
    _rule_outline_right: tuple[str, Style] | None = None
    _rule_outline_bottom: tuple[str, Style] | None = None
    _rule_outline_left: tuple[str, Style] | None = None

    _rule_size: int | None = None
    _rule_fraction: int | None = None
    _rule_min_size: int | None = None

    _rule_dock_group: str | None = None
    _rule_dock_edge: str | None = None
    _rule_docks: tuple[str, ...] | None = None

    _rule_layers: str | None = None
    _rule_layer: tuple[str, ...] | None = None

    important: set[str] = field(default_factory=set)

    display = StringProperty(VALID_DISPLAY, "block")
    visibility = StringProperty(VALID_VISIBILITY, "visible")
    layout = StringProperty(VALID_LAYOUT, "dock")

    text = StyleProperty()

    padding = SpacingProperty()
    margin = SpacingProperty()
    offset = OffsetProperty()

    border = BorderProperty()
    border_top = BoxProperty()
    border_right = BoxProperty()
    border_bottom = BoxProperty()
    border_left = BoxProperty()

    outline = BorderProperty()
    outline_top = BoxProperty()
    outline_right = BoxProperty()
    outline_bottom = BoxProperty()
    outline_left = BoxProperty()

    size = IntegerProperty()
    fraction = IntegerProperty()
    min_size = IntegerProperty()

    dock_group = DockGroupProperty()
    docks = DocksProperty()
    dock_edge = DockEdgeProperty()

    layer = NameProperty()
    layers = NameListProperty()

    @property
    def has_border(self) -> bool:
        """Check in a border is present."""
        return any(edge for edge, _style in self.border)

    @property
    def has_outline(self) -> bool:
        """Check if an outline is present."""
        return any(edge for edge, _style in self.outline)

    def extract_rules(
        self, specificity: tuple[int, int, int]
    ) -> dict[str, tuple[tuple[int, int, int, int], object]]:
        is_important = self.important.__contains__
        return {
            rule_name: (
                (int(is_important(rule_name)), *specificity),
                getattr(self, rule_name),
            )
            for rule_name in RULE_NAMES
            if getattr(self, f"_rule_{rule_name}") is not None
        }

    def __rich_repr__(self) -> rich.repr.Result:
        if self.has_border:
            yield "border", self.border
        yield "display", self.display, "block"
        yield "dock_edge", self.dock_edge, ""
        yield "dock_group", self.dock_group, ""
        yield "docks", self.docks, ()
        yield "margin", self.margin, NULL_SPACING
        yield "offset", self.offset, NULL_OFFSET
        if self.has_outline:
            yield "outline", self.outline
        yield "padding", self.padding, NULL_SPACING
        yield "text", self.text, ""
        yield "visibility", self.visibility, "visible"
        yield "layers", self.layers, ()
        yield "layer", self.layer, ""

        if self.important:
            yield "important", self.important

    @property
    def css_lines(self) -> list[str]:
        lines: list[str] = []
        append = lines.append

        def append_declaration(name: str, value: str) -> None:
            if name in self.important:
                append(f"{name}: {value} !important;")
            else:
                append(f"{name}: {value};")

        if self._rule_display is not None:
            append_declaration("display", self._rule_display)
        if self._rule_visibility is not None:
            append_declaration("visibility", self._rule_visibility)
        if self._rule_text is not None:
            append_declaration("text", str(self._rule_text))
        if self._rule_padding is not None:
            append_declaration("padding", self._rule_padding.packed)
        if self._rule_margin is not None:
            append_declaration("margin", self._rule_margin.packed)

        if (
            self._rule_border_top is not None
            and self._rule_border_top == self._rule_border_right
            and self._rule_border_right == self._rule_border_bottom
            and self._rule_border_bottom == self._rule_border_left
        ):
            _type, style = self._rule_border_top
            append_declaration("border", f"{_type} {style}")
        else:
            if self._rule_border_top is not None:
                _type, style = self._rule_border_top
                append_declaration("border-top", f"{_type} {style}")
            if self._rule_border_right is not None:
                _type, style = self._rule_border_right
                append_declaration("border-right", f"{_type} {style}")
            if self._rule_border_bottom is not None:
                _type, style = self._rule_border_bottom
                append_declaration("border-bottom", f"{_type} {style}")
            if self._rule_border_left is not None:
                _type, style = self._rule_border_left
                append_declaration("border-left", f"{_type} {style}")

        if (
            self._rule_outline_top is not None
            and self._rule_outline_top == self._rule_outline_right
            and self._rule_outline_right == self._rule_outline_bottom
            and self._rule_outline_bottom == self._rule_outline_left
        ):
            _type, style = self._rule_outline_top
            append_declaration("outline", f"{_type} {style}")
        else:
            if self._rule_outline_top is not None:
                _type, style = self._rule_outline_top
                append_declaration("outline-top", f"{_type} {style}")
            if self._rule_outline_right is not None:
                _type, style = self._rule_outline_right
                append_declaration("outline-right", f"{_type} {style}")
            if self._rule_outline_bottom is not None:
                _type, style = self._rule_outline_bottom
                append_declaration("outline-bottom", f"{_type} {style}")
            if self._rule_outline_left is not None:
                _type, style = self._rule_outline_left
                append_declaration("outline-left", f"{_type} {style}")

        if self.offset:
            x, y = self.offset
            append_declaration("offset", f"{x} {y}")
        if self._rule_dock_group:
            append_declaration("dock-group", self._rule_dock_group)
        if self._rule_docks:
            append_declaration("docks", " ".join(self._rule_docks))
        if self._rule_dock_edge:
            append_declaration("dock-edge", self._rule_dock_edge)
        if self._rule_layers is not None:
            append_declaration("layers", " ".join(self.layers))
        if self._rule_layer is not None:
            append_declaration("layer", self.layer)

        lines.sort()
        return lines

    @property
    def css(self) -> str:
        return "\n".join(self.css_lines)


RULE_NAMES = {name[6:] for name in dir(Styles) if name.startswith("_rule_")}

if __name__ == "__main__":
    styles = Styles()

    styles.display = "none"
    styles.visibility = "hidden"
    styles.border = ("solid", "rgb(10,20,30)")
    styles.outline_right = ("solid", "red")
    styles.docks = "foo bar"
    styles.text = "italic blue"
    styles.dock_group = "bar"
    styles.layers = "foo bar"

    from rich import inspect, print

    print(styles)
    print(styles.css)
    print(dir(styles))
    print(RULE_NAMES)

    print(styles.extract_rules((0, 1, 0)))
