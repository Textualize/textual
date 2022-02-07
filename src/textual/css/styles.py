from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any, Iterable, NamedTuple, TYPE_CHECKING

import rich.repr
from rich.color import Color
from rich.style import Style

from ._style_properties import (
    BorderProperty,
    BoxProperty,
    ColorProperty,
    DocksProperty,
    DockProperty,
    OffsetProperty,
    NameProperty,
    NameListProperty,
    ScalarProperty,
    SpacingProperty,
    StringEnumProperty,
    StyleProperty,
    StyleFlagsProperty,
    TransitionsProperty,
    LayoutProperty,
)
from .constants import (
    VALID_DISPLAY,
    VALID_VISIBILITY,
)
from .scalar import Scalar, ScalarOffset, Unit
from .scalar_animation import ScalarAnimation
from .transition import Transition
from .types import Display, Edge, Visibility
from .types import Specificity3, Specificity4
from .._animator import Animation, EasingFunction
from ..geometry import Spacing

if TYPE_CHECKING:
    from ..layout import Layout
    from ..dom import DOMNode


class DockGroup(NamedTuple):
    name: str
    edge: Edge
    z: int


@rich.repr.auto
@dataclass
class Styles:

    node: DOMNode | None = None

    _rule_display: Display | None = None
    _rule_visibility: Visibility | None = None
    _rule_layout: "Layout" | None = None

    _rule_text_color: Color | None = None
    _rule_text_background: Color | None = None
    _rule_text_style: Style | None = None

    _rule_padding: Spacing | None = None
    _rule_margin: Spacing | None = None
    _rule_offset: ScalarOffset | None = None

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

    _rule_dock: str | None = None
    _rule_docks: tuple[DockGroup, ...] | None = None

    _rule_layers: tuple[str, ...] | None = None
    _rule_layer: str | None = None

    _rule_transitions: dict[str, Transition] | None = None

    _layout_required: bool = False
    _repaint_required: bool = False

    important: set[str] = field(default_factory=set)

    display = StringEnumProperty(VALID_DISPLAY, "block")
    visibility = StringEnumProperty(VALID_VISIBILITY, "visible")
    layout = LayoutProperty()

    text = StyleProperty()
    text_color = ColorProperty()
    text_background = ColorProperty()
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

    width = ScalarProperty(percent_unit=Unit.WIDTH)
    height = ScalarProperty(percent_unit=Unit.HEIGHT)
    min_width = ScalarProperty(percent_unit=Unit.WIDTH)
    min_height = ScalarProperty(percent_unit=Unit.HEIGHT)

    dock = DockProperty()
    docks = DocksProperty()

    layer = NameProperty()
    layers = NameListProperty()
    transitions = TransitionsProperty()

    ANIMATABLE = {
        "offset",
        "padding",
        "margin",
        "width",
        "height",
        "min_width",
        "min_height",
    }

    @property
    def gutter(self) -> Spacing:
        """Get the gutter (additional space reserved for margin / padding / border).

        Returns:
            Spacing: Space around edges.
        """
        gutter = self.margin + self.padding + self.border.spacing
        return gutter

    @classmethod
    @lru_cache(maxsize=1024)
    def parse(cls, css: str, path: str) -> Styles:
        from .parse import parse_declarations

        styles = parse_declarations(css, path)
        return styles

    def __textual_animation__(
        self,
        attribute: str,
        value: Any,
        start_time: float,
        duration: float | None,
        speed: float | None,
        easing: EasingFunction,
    ) -> Animation | None:
        from ..widget import Widget

        assert isinstance(self.node, Widget)
        if isinstance(value, ScalarOffset):
            return ScalarAnimation(
                self.node,
                self,
                start_time,
                attribute,
                value,
                duration=duration,
                speed=speed,
                easing=easing,
            )
        return None

    def refresh(self, layout: bool = False) -> None:
        self._repaint_required = True
        self._layout_required = layout

    def check_refresh(self) -> tuple[bool, bool]:
        result = (self._repaint_required, self._layout_required)
        self._repaint_required = self._layout_required = False
        return result

    @property
    def has_border(self) -> bool:
        """Check in a border is present."""
        return any(edge for edge, _style in self.border)

    @property
    def has_padding(self) -> bool:
        return self._rule_padding is not None

    @property
    def has_margin(self) -> bool:
        return self._rule_margin is not None

    @property
    def has_outline(self) -> bool:
        """Check if an outline is present."""
        return any(edge for edge, _style in self.outline)

    @property
    def has_offset(self) -> bool:
        return self._rule_offset is not None

    def get_transition(self, key: str) -> Transition | None:
        if key in self.ANIMATABLE:
            return self.transitions.get(key, None)
        else:
            return None

    def reset(self) -> None:
        """
        Reset internal style rules to ``None``, reverting to default styles.
        """
        for rule_name in INTERNAL_RULE_NAMES:
            setattr(self, rule_name, None)

    def extract_rules(
        self, specificity: Specificity3
    ) -> list[tuple[str, Specificity4, Any]]:
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

    def apply_rules(self, rules: Iterable[tuple[str, object]], animate: bool = False):
        if animate or self.node is None:
            for key, value in rules:
                setattr(self, f"_rule_{key}", value)
        else:
            styles = self
            is_animatable = styles.ANIMATABLE.__contains__
            for key, value in rules:
                current = getattr(styles, f"_rule_{key}")
                if current == value:
                    continue
                if is_animatable(key):
                    transition = styles.get_transition(key)
                    if transition is None:
                        setattr(styles, f"_rule_{key}", value)
                    else:
                        duration, easing, delay = transition
                        self.node.app.animator.animate(
                            styles, key, value, duration=duration, easing=easing
                        )
                else:
                    setattr(styles, f"_rule_{key}", value)

        if self.node is not None:
            self.node.on_style_change()

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
        if self._rule_dock:
            append_declaration("dock-group", self._rule_dock)
        if self._rule_docks:
            append_declaration(
                "docks",
                " ".join(
                    (f"{name}={edge}/{z}" if z else f"{name}={edge}")
                    for name, edge, z in self._rule_docks
                ),
            )
        if self._rule_layers is not None:
            append_declaration("layers", " ".join(self.layers))
        if self._rule_layer is not None:
            append_declaration("layer", self.layer)
        if self._rule_text_color or self._rule_text_background or self._rule_text_style:
            append_declaration("text", str(self.text))

        if self._rule_width is not None:
            append_declaration("width", str(self.width))
        if self._rule_height is not None:
            append_declaration("height", str(self.height))
        if self._rule_min_width is not None:
            append_declaration("min-width", str(self.min_width))
        if self._rule_min_height is not None:
            append_declaration("min-height", str(self.min_height))
        if self._rule_transitions is not None:
            append_declaration(
                "transition",
                ", ".join(
                    f"{name} {transition}"
                    for name, transition in self.transitions.items()
                ),
            )

        lines.sort()
        return lines

    @property
    def css(self) -> str:
        return "\n".join(self.css_lines)


RULE_NAMES = [name[6:] for name in dir(Styles) if name.startswith("_rule_")]
INTERNAL_RULE_NAMES = [f"_rule_{name}" for name in RULE_NAMES]

if __name__ == "__main__":
    styles = Styles()

    styles.display = "none"
    styles.visibility = "hidden"
    styles.border = ("solid", "rgb(10,20,30)")
    styles.outline_right = ("solid", "red")
    styles.docks = "foo bar"
    styles.text_style = "italic"
    styles.dock = "bar"
    styles.layers = "foo bar"

    from rich import print

    print(styles.text_style)
    print(styles.text)

    print(styles)
    print(styles.css)

    print(styles.extract_rules((0, 1, 0)))
