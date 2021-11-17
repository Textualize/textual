from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable

from rich import print
from rich.color import Color
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
from .scalar import Scalar
from ._style_properties import (
    BorderProperty,
    BoxProperty,
    ColorProperty,
    DockEdgeProperty,
    DocksProperty,
    DockGroupProperty,
    OffsetProperty,
    NameProperty,
    NameListProperty,
    ScalarProperty,
    SpacingProperty,
    StringProperty,
    StyleProperty,
    StyleFlagsProperty,
)
from .types import Display, Visibility


@dataclass
class Styles:

    _rule_display: Display | None = None
    _rule_visibility: Visibility | None = None
    _rule_layout: str | None = None

    _rule_text_color: Color | None = None
    _rule_text_bgcolor: Color | None = None
    _rule_text_style: Style | None = None

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

    _rule_width: Scalar | None = None
    _rule_height: Scalar | None = None
    _rule_min_width: Scalar | None = None
    _rule_min_height: Scalar | None = None

    _rule_layout: str | None = None

    _rule_dock_group: str | None = None
    _rule_dock_edge: str | None = None
    _rule_docks: tuple[tuple[str, str], ...] | None = None

    _rule_layers: str | None = None
    _rule_layer: tuple[str, ...] | None = None

    important: set[str] = field(default_factory=set)

    display = StringProperty(VALID_DISPLAY, "block")
    visibility = StringProperty(VALID_VISIBILITY, "visible")
    layout = StringProperty(VALID_LAYOUT, "dock")

    text = StyleProperty()
    text_color = ColorProperty()
    text_bgcolor = ColorProperty()
    text_style = StyleFlagsProperty()

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

    width = ScalarProperty()
    height = ScalarProperty()
    min_width = ScalarProperty()
    min_height = ScalarProperty()

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
    ) -> list[tuple[str, tuple[int, int, int, int], Any]]:
        is_important = self.important.__contains__
        rules = [
            (
                rule_name,
                (int(is_important(rule_name)), *specificity),
                getattr(self, f"_rule_{rule_name}"),
            )
            for rule_name in RULE_NAMES
            if getattr(self, f"_rule_{rule_name}") is not None
        ]
        return rules

    def apply_rules(self, rules: Iterable[tuple[str, Any]]):
        for key, value in rules:
            setattr(self, f"_rule_{key}", value)

    def __rich_repr__(self) -> rich.repr.Result:
        for rule_name, internal_rule_name in zip(RULE_NAMES, INTERNAL_RULE_NAMES):
            if getattr(self, internal_rule_name) is not None:
                yield rule_name, getattr(self, rule_name)
        if self.important:
            yield "important", self.important

    @classmethod
    def combine(cls, style1: Styles, style2: Styles) -> Styles:
        """Combine rule with another to produce a new rule.

        Args:
            style1 (Style): A style.
            style2 (Style): Second style.

        Returns:
            Style: New rule with attributes of style2 overriding style1
        """
        result = cls()
        for name in INTERNAL_RULE_NAMES:
            setattr(result, name, getattr(style1, name) or getattr(style2, name))
        return result

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
            append_declaration(
                "docks",
                " ".join(
                    (f"{key}={value}" if value else key)
                    for key, value in self._rule_docks
                ),
            )
        if self._rule_dock_edge:
            append_declaration("dock-edge", self._rule_dock_edge)
        if self._rule_layers is not None:
            append_declaration("layers", " ".join(self.layers))
        if self._rule_layer is not None:
            append_declaration("layer", self.layer)
        if self._rule_text_color or self._rule_text_bgcolor or self._rule_text_style:
            append_declaration("text", str(self.text))

        if self._rule_width is not None:
            append_declaration("width", str(self.width))
        if self._rule_height is not None:
            append_declaration("height", str(self.height))
        if self._rule_min_width is not None:
            append_declaration("min-width", str(self.min_width))
        if self._rule_min_height is not None:
            append_declaration("min-height", str(self.min_height))

        lines.sort()
        return lines

    @property
    def css(self) -> str:
        return "\n".join(self.css_lines)


RULE_NAMES = {name[6:] for name in dir(Styles) if name.startswith("_rule_")}
INTERNAL_RULE_NAMES = {name for name in dir(Styles) if name.startswith("_rule_")}

if __name__ == "__main__":
    styles = Styles()

    styles.display = "none"
    styles.visibility = "hidden"
    styles.border = ("solid", "rgb(10,20,30)")
    styles.outline_right = ("solid", "red")
    styles.docks = "foo bar"
    styles.text_style = "italic"
    styles.dock_group = "bar"
    styles.layers = "foo bar"

    from rich import inspect, print

    print(styles.text_style)
    print(styles.text)

    print(styles)
    print(styles.css)

    print(styles.extract_rules((0, 1, 0)))
