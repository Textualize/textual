from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from functools import lru_cache, partial
from operator import attrgetter
from typing import TYPE_CHECKING, Any, Iterable, NamedTuple, cast

import rich.repr
from rich.style import Style
from typing_extensions import TypedDict

from .._animator import DEFAULT_EASING, Animatable, BoundAnimator, EasingFunction
from .._types import AnimationLevel, CallbackType
from ..color import Color
from ..geometry import Offset, Spacing
from ._style_properties import (
    AlignProperty,
    BooleanProperty,
    BorderProperty,
    BoxProperty,
    ColorProperty,
    DockProperty,
    FractionalProperty,
    IntegerProperty,
    KeylineProperty,
    LayoutProperty,
    NameListProperty,
    NameProperty,
    OffsetProperty,
    OverflowProperty,
    ScalarListProperty,
    ScalarProperty,
    ScrollbarColorProperty,
    SpacingProperty,
    StringEnumProperty,
    StyleFlagsProperty,
    TransitionsProperty,
)
from .constants import (
    VALID_ALIGN_HORIZONTAL,
    VALID_ALIGN_VERTICAL,
    VALID_BOX_SIZING,
    VALID_CONSTRAIN,
    VALID_DISPLAY,
    VALID_OVERFLOW,
    VALID_OVERLAY,
    VALID_SCROLLBAR_GUTTER,
    VALID_TEXT_ALIGN,
    VALID_VISIBILITY,
)
from .scalar import Scalar, ScalarOffset, Unit
from .scalar_animation import ScalarAnimation
from .transition import Transition
from .types import (
    AlignHorizontal,
    AlignVertical,
    BoxSizing,
    Constrain,
    Display,
    Edge,
    Overflow,
    Overlay,
    ScrollbarGutter,
    Specificity3,
    Specificity6,
    TextAlign,
    Visibility,
)

if TYPE_CHECKING:
    from .._layout import Layout
    from ..dom import DOMNode
    from .types import CSSLocation


class RulesMap(TypedDict, total=False):
    """A typed dict for CSS rules.

    Any key may be absent, indicating that rule has not been set.

    Does not define composite rules, that is a rule that is made of a combination of other rules.
    """

    display: Display
    visibility: Visibility
    layout: "Layout"

    auto_color: bool
    color: Color
    background: Color
    text_style: Style

    opacity: float
    text_opacity: float

    padding: Spacing
    margin: Spacing
    offset: ScalarOffset

    border_top: tuple[str, Color]
    border_right: tuple[str, Color]
    border_bottom: tuple[str, Color]
    border_left: tuple[str, Color]

    border_title_align: AlignHorizontal
    border_subtitle_align: AlignHorizontal

    outline_top: tuple[str, Color]
    outline_right: tuple[str, Color]
    outline_bottom: tuple[str, Color]
    outline_left: tuple[str, Color]

    keyline: tuple[str, Color]

    box_sizing: BoxSizing
    width: Scalar
    height: Scalar
    min_width: Scalar
    min_height: Scalar
    max_width: Scalar
    max_height: Scalar

    dock: str

    overflow_x: Overflow
    overflow_y: Overflow

    layers: tuple[str, ...]
    layer: str

    transitions: dict[str, Transition]

    tint: Color

    scrollbar_color: Color
    scrollbar_color_hover: Color
    scrollbar_color_active: Color

    scrollbar_corner_color: Color

    scrollbar_background: Color
    scrollbar_background_hover: Color
    scrollbar_background_active: Color

    scrollbar_gutter: ScrollbarGutter

    scrollbar_size_vertical: int
    scrollbar_size_horizontal: int

    align_horizontal: AlignHorizontal
    align_vertical: AlignVertical

    content_align_horizontal: AlignHorizontal
    content_align_vertical: AlignVertical

    grid_size_rows: int
    grid_size_columns: int
    grid_gutter_horizontal: int
    grid_gutter_vertical: int
    grid_rows: tuple[Scalar, ...]
    grid_columns: tuple[Scalar, ...]

    row_span: int
    column_span: int

    text_align: TextAlign

    link_color: Color
    auto_link_color: bool
    link_background: Color
    link_style: Style

    link_color_hover: Color
    auto_link_color_hover: bool
    link_background_hover: Color
    link_style_hover: Style

    auto_border_title_color: bool
    border_title_color: Color
    border_title_background: Color
    border_title_style: Style

    auto_border_subtitle_color: bool
    border_subtitle_color: Color
    border_subtitle_background: Color
    border_subtitle_style: Style

    overlay: Overlay
    constrain: Constrain


RULE_NAMES = list(RulesMap.__annotations__.keys())
RULE_NAMES_SET = frozenset(RULE_NAMES)
_rule_getter = attrgetter(*RULE_NAMES)


class DockGroup(NamedTuple):
    name: str
    edge: Edge
    z: int


class StylesBase(ABC):
    """A common base class for Styles and RenderStyles"""

    ANIMATABLE = {
        "offset",
        "padding",
        "margin",
        "width",
        "height",
        "min_width",
        "min_height",
        "max_width",
        "max_height",
        "auto_color",
        "color",
        "background",
        "opacity",
        "text_opacity",
        "tint",
        "scrollbar_color",
        "scrollbar_color_hover",
        "scrollbar_color_active",
        "scrollbar_background",
        "scrollbar_background_hover",
        "scrollbar_background_active",
        "link_color",
        "link_background",
        "link_color_hover",
        "link_background_hover",
    }

    node: DOMNode | None = None

    display = StringEnumProperty(
        VALID_DISPLAY, "block", layout=True, refresh_parent=True, refresh_children=True
    )
    visibility = StringEnumProperty(
        VALID_VISIBILITY, "visible", layout=True, refresh_parent=True
    )
    layout = LayoutProperty()

    auto_color = BooleanProperty(default=False)
    color = ColorProperty(Color(255, 255, 255))
    background = ColorProperty(Color(0, 0, 0, 0))
    text_style = StyleFlagsProperty()

    opacity = FractionalProperty(children=True)
    text_opacity = FractionalProperty()

    padding = SpacingProperty()
    margin = SpacingProperty()
    offset = OffsetProperty()

    border = BorderProperty(layout=True)
    border_top = BoxProperty(Color(0, 255, 0))
    border_right = BoxProperty(Color(0, 255, 0))
    border_bottom = BoxProperty(Color(0, 255, 0))
    border_left = BoxProperty(Color(0, 255, 0))

    border_title_align = StringEnumProperty(VALID_ALIGN_HORIZONTAL, "left")
    border_subtitle_align = StringEnumProperty(VALID_ALIGN_HORIZONTAL, "right")

    outline = BorderProperty(layout=False)
    outline_top = BoxProperty(Color(0, 255, 0))
    outline_right = BoxProperty(Color(0, 255, 0))
    outline_bottom = BoxProperty(Color(0, 255, 0))
    outline_left = BoxProperty(Color(0, 255, 0))

    keyline = KeylineProperty()

    box_sizing = StringEnumProperty(VALID_BOX_SIZING, "border-box", layout=True)
    width = ScalarProperty(percent_unit=Unit.WIDTH)
    height = ScalarProperty(percent_unit=Unit.HEIGHT)
    min_width = ScalarProperty(percent_unit=Unit.WIDTH, allow_auto=False)
    min_height = ScalarProperty(percent_unit=Unit.HEIGHT, allow_auto=False)
    max_width = ScalarProperty(percent_unit=Unit.WIDTH, allow_auto=False)
    max_height = ScalarProperty(percent_unit=Unit.HEIGHT, allow_auto=False)

    dock = DockProperty()

    overflow_x = OverflowProperty(VALID_OVERFLOW, "hidden")
    overflow_y = OverflowProperty(VALID_OVERFLOW, "hidden")

    layer = NameProperty()
    layers = NameListProperty()
    transitions = TransitionsProperty()

    tint = ColorProperty("transparent")
    scrollbar_color = ScrollbarColorProperty("ansi_bright_magenta")
    scrollbar_color_hover = ScrollbarColorProperty("ansi_yellow")
    scrollbar_color_active = ScrollbarColorProperty("ansi_bright_yellow")

    scrollbar_corner_color = ScrollbarColorProperty("#666666")

    scrollbar_background = ScrollbarColorProperty("#555555")
    scrollbar_background_hover = ScrollbarColorProperty("#444444")
    scrollbar_background_active = ScrollbarColorProperty("black")

    scrollbar_gutter = StringEnumProperty(
        VALID_SCROLLBAR_GUTTER, "auto", layout=True, refresh_children=True
    )

    scrollbar_size_vertical = IntegerProperty(default=1, layout=True)
    scrollbar_size_horizontal = IntegerProperty(default=1, layout=True)

    align_horizontal = StringEnumProperty(
        VALID_ALIGN_HORIZONTAL, "left", layout=True, refresh_children=True
    )
    align_vertical = StringEnumProperty(
        VALID_ALIGN_VERTICAL, "top", layout=True, refresh_children=True
    )
    align = AlignProperty()

    content_align_horizontal = StringEnumProperty(VALID_ALIGN_HORIZONTAL, "left")
    content_align_vertical = StringEnumProperty(VALID_ALIGN_VERTICAL, "top")
    content_align = AlignProperty()

    grid_rows = ScalarListProperty(percent_unit=Unit.HEIGHT, refresh_children=True)
    grid_columns = ScalarListProperty(percent_unit=Unit.WIDTH, refresh_children=True)

    grid_size_columns = IntegerProperty(default=1, layout=True, refresh_children=True)
    grid_size_rows = IntegerProperty(default=0, layout=True, refresh_children=True)
    grid_gutter_horizontal = IntegerProperty(
        default=0, layout=True, refresh_children=True
    )
    grid_gutter_vertical = IntegerProperty(
        default=0, layout=True, refresh_children=True
    )

    row_span = IntegerProperty(default=1, layout=True)
    column_span = IntegerProperty(default=1, layout=True)

    text_align = StringEnumProperty(VALID_TEXT_ALIGN, "start")

    link_color = ColorProperty("transparent")
    auto_link_color = BooleanProperty(False)
    link_background = ColorProperty("transparent")
    link_style = StyleFlagsProperty()

    link_color_hover = ColorProperty("transparent")
    auto_link_color_hover = BooleanProperty(False)
    link_background_hover = ColorProperty("transparent")
    link_style_hover = StyleFlagsProperty()

    auto_border_title_color = BooleanProperty(default=False)
    border_title_color = ColorProperty(Color(255, 255, 255, 0))
    border_title_background = ColorProperty(Color(0, 0, 0, 0))
    border_title_style = StyleFlagsProperty()

    auto_border_subtitle_color = BooleanProperty(default=False)
    border_subtitle_color = ColorProperty(Color(255, 255, 255, 0))
    border_subtitle_background = ColorProperty(Color(0, 0, 0, 0))
    border_subtitle_style = StyleFlagsProperty()

    overlay = StringEnumProperty(
        VALID_OVERLAY, "none", layout=True, refresh_parent=True
    )
    constrain = StringEnumProperty(VALID_CONSTRAIN, "none")

    def __textual_animation__(
        self,
        attribute: str,
        start_value: object,
        value: object,
        start_time: float,
        duration: float | None,
        speed: float | None,
        easing: EasingFunction,
        on_complete: CallbackType | None = None,
        level: AnimationLevel = "full",
    ) -> ScalarAnimation | None:
        if self.node is None:
            return None

        # Check we are animating a Scalar or Scalar offset
        if isinstance(start_value, (Scalar, ScalarOffset)):
            # If destination is a number, we can convert that to a scalar
            if isinstance(value, (int, float)):
                value = Scalar(value, Unit.CELLS, Unit.CELLS)

            # We can only animate to Scalar
            if not isinstance(value, (Scalar, ScalarOffset)):
                return None

            from ..widget import Widget

            assert isinstance(self.node, Widget)
            return ScalarAnimation(
                self.node,
                self,
                start_time,
                attribute,
                value,
                duration=duration,
                speed=speed,
                easing=easing,
                on_complete=(
                    partial(self.node.app.call_later, on_complete)
                    if on_complete is not None
                    else None
                ),
                level=level,
            )
        return None

    def __eq__(self, styles: object) -> bool:
        """Check that Styles contains the same rules."""
        if not isinstance(styles, StylesBase):
            return NotImplemented
        return self.get_rules() == styles.get_rules()

    @property
    def gutter(self) -> Spacing:
        """Get space around widget.

        Returns:
            Space around widget content.
        """
        return self.padding + self.border.spacing

    @property
    def auto_dimensions(self) -> bool:
        """Check if width or height are set to 'auto'."""
        has_rule = self.has_rule
        return (has_rule("width") and self.width.is_auto) or (  # type: ignore
            has_rule("height") and self.height.is_auto  # type: ignore
        )

    @property
    def is_relative_width(self) -> bool:
        """Does the node have a relative width?"""
        width = self.width
        return width is not None and width.unit in (Unit.FRACTION, Unit.PERCENT)

    @property
    def is_relative_height(self) -> bool:
        """Does the node have a relative width?"""
        height = self.height
        return height is not None and height.unit in (Unit.FRACTION, Unit.PERCENT)

    @abstractmethod
    def has_rule(self, rule: str) -> bool:
        """Check if a rule is set on this Styles object.

        Args:
            rule: Rule name.

        Returns:
            ``True`` if the rules is present, otherwise ``False``.
        """

    @abstractmethod
    def clear_rule(self, rule: str) -> bool:
        """Removes the rule from the Styles object, as if it had never been set.

        Args:
            rule: Rule name.

        Returns:
            ``True`` if a rule was cleared, or ``False`` if the rule is already not set.
        """

    @abstractmethod
    def get_rules(self) -> RulesMap:
        """Get the rules in a mapping.

        Returns:
            A TypedDict of the rules.
        """

    @abstractmethod
    def set_rule(self, rule: str, value: object | None) -> bool:
        """Set a rule.

        Args:
            rule: Rule name.
            value: New rule value.

        Returns:
            ``True`` if the rule changed, otherwise ``False``.
        """

    @abstractmethod
    def get_rule(self, rule: str, default: object = None) -> object:
        """Get an individual rule.

        Args:
            rule: Name of rule.
            default: Default if rule does not exists.

        Returns:
            Rule value or default.
        """

    @abstractmethod
    def refresh(
        self, *, layout: bool = False, children: bool = False, parent: bool = False
    ) -> None:
        """Mark the styles as requiring a refresh.

        Args:
            layout: Also require a layout.
            children: Also refresh children.
            parent: Also refresh the parent.
        """

    @abstractmethod
    def reset(self) -> None:
        """Reset the rules to initial state."""

    @abstractmethod
    def merge(self, other: StylesBase) -> None:
        """Merge values from another Styles.

        Args:
            other: A Styles object.
        """

    @abstractmethod
    def merge_rules(self, rules: RulesMap) -> None:
        """Merge rules in to Styles.

        Args:
            rules: A mapping of rules.
        """

    def get_render_rules(self) -> RulesMap:
        """Get rules map with defaults."""
        # Get a dictionary of rules, going through the properties
        rules = dict(zip(RULE_NAMES, _rule_getter(self)))
        return cast(RulesMap, rules)

    @classmethod
    def is_animatable(cls, rule: str) -> bool:
        """Check if a given rule may be animated.

        Args:
            rule: Name of the rule.

        Returns:
            ``True`` if the rule may be animated, otherwise ``False``.
        """
        return rule in cls.ANIMATABLE

    @classmethod
    @lru_cache(maxsize=1024)
    def parse(
        cls, css: str, read_from: CSSLocation, *, node: DOMNode | None = None
    ) -> Styles:
        """Parse CSS and return a Styles object.

        Args:
            css: Textual CSS.
            read_from: Location where the CSS was read from.
            node: Node to associate with the Styles.

        Returns:
            A Styles instance containing result of parsing CSS.
        """
        from .parse import parse_declarations

        styles = parse_declarations(css, read_from)
        styles.node = node
        return styles

    def _get_transition(self, key: str) -> Transition | None:
        """Get a transition.

        Args:
            key: Transition key.

        Returns:
            Transition object or None it no transition exists.
        """
        if key in self.ANIMATABLE:
            return self.transitions.get(key, None)
        else:
            return None

    def _align_width(self, width: int, parent_width: int) -> int:
        """Align the width dimension.

        Args:
            width: Width of the content.
            parent_width: Width of the parent container.

        Returns:
            An offset to add to the X coordinate.
        """
        offset_x = 0
        align_horizontal = self.align_horizontal
        if align_horizontal != "left":
            if align_horizontal == "center":
                offset_x = (parent_width - width) // 2
            else:
                offset_x = parent_width - width
        return offset_x

    def _align_height(self, height: int, parent_height: int) -> int:
        """Align the height dimensions

        Args:
            height: Height of the content.
            parent_height: Height of the parent container.

        Returns:
            An offset to add to the Y coordinate.
        """
        offset_y = 0
        align_vertical = self.align_vertical
        if align_vertical != "top":
            if align_vertical == "middle":
                offset_y = (parent_height - height) // 2
            else:
                offset_y = parent_height - height
        return offset_y

    def _align_size(self, child: tuple[int, int], parent: tuple[int, int]) -> Offset:
        """Align a size according to alignment rules.

        Args:
            child: The size of the child (width, height)
            parent: The size of the parent (width, height)

        Returns:
            Offset required to align the child.
        """
        width, height = child
        parent_width, parent_height = parent
        return Offset(
            self._align_width(width, parent_width),
            self._align_height(height, parent_height),
        )

    @property
    def partial_rich_style(self) -> Style:
        """Get the style properties associated with this node only (not including parents in the DOM).

        Returns:
            Rich Style object.
        """
        style = Style(
            color=(self.color.rich_color if self.has_rule("color") else None),
            bgcolor=(
                self.background.rich_color if self.has_rule("background") else None
            ),
        )
        style += self.text_style
        return style


@rich.repr.auto
@dataclass
class Styles(StylesBase):
    node: DOMNode | None = None
    _rules: RulesMap = field(
        default_factory=RulesMap
    )  # mypy won't be happy with `default_factory=RulesMap`
    _updates: int = 0

    important: set[str] = field(default_factory=set)

    def copy(self) -> Styles:
        """Get a copy of this Styles object."""
        return Styles(
            node=self.node,
            _rules=self.get_rules(),
            important=self.important,
        )

    def has_rule(self, rule: str) -> bool:
        assert rule in RULE_NAMES_SET, f"no such rule {rule!r}"
        return rule in self._rules

    def clear_rule(self, rule: str) -> bool:
        """Removes the rule from the Styles object, as if it had never been set.

        Args:
            rule: Rule name.

        Returns:
            ``True`` if a rule was cleared, or ``False`` if it was already not set.
        """
        changed = self._rules.pop(rule, None) is not None  # type: ignore
        if changed:
            self._updates += 1
        return changed

    def get_rules(self) -> RulesMap:
        return self._rules.copy()

    def set_rule(self, rule: str, value: object | None) -> bool:
        """Set a rule.

        Args:
            rule: Rule name.
            value: New rule value.

        Returns:
            ``True`` if the rule changed, otherwise ``False``.
        """
        if value is None:
            changed = self._rules.pop(rule, None) is not None  # type: ignore
            if changed:
                self._updates += 1
            return changed
        current = self._rules.get(rule)
        self._rules[rule] = value  # type: ignore
        changed = current != value
        if changed:
            self._updates += 1
        return changed

    def get_rule(self, rule: str, default: object = None) -> object:
        return self._rules.get(rule, default)

    def refresh(
        self, *, layout: bool = False, children: bool = False, parent: bool = False
    ) -> None:
        node = self.node
        if node is None or not node._is_mounted:
            return
        if parent and node._parent is not None:
            node._parent.refresh()
        node.refresh(layout=layout)
        if children:
            for child in node.walk_children(with_self=False, reverse=True):
                child.refresh(layout=layout)

    def reset(self) -> None:
        """Reset the rules to initial state."""
        self._updates += 1
        self._rules.clear()  # type: ignore

    def merge(self, other: StylesBase) -> None:
        """Merge values from another Styles.

        Args:
            other: A Styles object.
        """
        self._updates += 1
        self._rules.update(other.get_rules())

    def merge_rules(self, rules: RulesMap) -> None:
        self._updates += 1
        self._rules.update(rules)

    def extract_rules(
        self,
        specificity: Specificity3,
        is_default_rules: bool = False,
        tie_breaker: int = 0,
    ) -> list[tuple[str, Specificity6, Any]]:
        """Extract rules from Styles object, and apply !important css specificity as
        well as higher specificity of user CSS vs widget CSS.

        Args:
            specificity: A node specificity.
            is_default_rules: True if the rules we're extracting are
                default (i.e. in Widget.DEFAULT_CSS) rules. False if they're from user defined CSS.

        Returns:
            A list containing a tuple of <RULE NAME>, <SPECIFICITY> <RULE VALUE>.
        """
        is_important = self.important.__contains__
        default_rules = 0 if is_default_rules else 1
        rules: list[tuple[str, Specificity6, Any]] = [
            (
                rule_name,
                (
                    default_rules,
                    1 if is_important(rule_name) else 0,
                    *specificity,
                    tie_breaker,
                ),
                rule_value,
            )
            for rule_name, rule_value in self._rules.items()
        ]

        return rules

    def __rich_repr__(self) -> rich.repr.Result:
        has_rule = self.has_rule
        for name in RULE_NAMES:
            if has_rule(name):
                yield name, getattr(self, name)
        if self.important:
            yield "important", self.important

    def _get_border_css_lines(
        self, rules: RulesMap, name: str
    ) -> Iterable[tuple[str, str]]:
        """Get pairs of strings containing <RULE NAME>, <RULE VALUE> for border css declarations.

        Args:
            rules: A rules map.
            name: Name of rules (border or outline)

        Returns:
            An iterable of CSS declarations.
        """

        has_rule = rules.__contains__
        get_rule = rules.__getitem__

        has_top = has_rule(f"{name}_top")
        has_right = has_rule(f"{name}_right")
        has_bottom = has_rule(f"{name}_bottom")
        has_left = has_rule(f"{name}_left")
        if not any((has_top, has_right, has_bottom, has_left)):
            # No border related rules
            return

        if all((has_top, has_right, has_bottom, has_left)):
            # All rules are set
            # See if we can set them with a single border: declaration
            top = get_rule(f"{name}_top")
            right = get_rule(f"{name}_right")
            bottom = get_rule(f"{name}_bottom")
            left = get_rule(f"{name}_left")

            if top == right and right == bottom and bottom == left:
                border_type, border_color = rules[f"{name}_top"]  # type: ignore
                yield name, f"{border_type} {border_color.hex}"
                return

        # Check for edges
        if has_top:
            border_type, border_color = rules[f"{name}_top"]  # type: ignore
            yield f"{name}-top", f"{border_type} {border_color.hex}"

        if has_right:
            border_type, border_color = rules[f"{name}_right"]  # type: ignore
            yield f"{name}-right", f"{border_type} {border_color.hex}"

        if has_bottom:
            border_type, border_color = rules[f"{name}_bottom"]  # type: ignore
            yield f"{name}-bottom", f"{border_type} {border_color.hex}"

        if has_left:
            border_type, border_color = rules[f"{name}_left"]  # type: ignore
            yield f"{name}-left", f"{border_type} {border_color.hex}"

    @property
    def css_lines(self) -> list[str]:
        lines: list[str] = []
        append = lines.append

        def append_declaration(name: str, value: str) -> None:
            if name in self.important:
                append(f"{name}: {value} !important;")
            else:
                append(f"{name}: {value};")

        rules = self.get_rules()
        get_rule = rules.get

        if "display" in rules:
            append_declaration("display", rules["display"])
        if "visibility" in rules:
            append_declaration("visibility", rules["visibility"])
        if "padding" in rules:
            append_declaration("padding", rules["padding"].css)
        if "margin" in rules:
            append_declaration("margin", rules["margin"].css)

        for name, rule in self._get_border_css_lines(rules, "border"):
            append_declaration(name, rule)

        for name, rule in self._get_border_css_lines(rules, "outline"):
            append_declaration(name, rule)

        if "offset" in rules:
            x, y = self.offset
            append_declaration("offset", f"{x} {y}")
        if "dock" in rules:
            append_declaration("dock", rules["dock"])
        if "layers" in rules:
            append_declaration("layers", " ".join(self.layers))
        if "layer" in rules:
            append_declaration("layer", self.layer)
        if "layout" in rules:
            assert self.layout is not None
            append_declaration("layout", self.layout.name)

        if "color" in rules:
            append_declaration("color", self.color.hex)
        if "background" in rules:
            append_declaration("background", self.background.hex)
        if "text_style" in rules:
            append_declaration("text-style", str(get_rule("text_style")))
        if "tint" in rules:
            append_declaration("tint", self.tint.css)

        if "overflow_x" in rules:
            append_declaration("overflow-x", self.overflow_x)
        if "overflow_y" in rules:
            append_declaration("overflow-y", self.overflow_y)

        if "scrollbar_color" in rules:
            append_declaration("scrollbar-color", self.scrollbar_color.css)
        if "scrollbar_color_hover" in rules:
            append_declaration("scrollbar-color-hover", self.scrollbar_color_hover.css)
        if "scrollbar_color_active" in rules:
            append_declaration(
                "scrollbar-color-active", self.scrollbar_color_active.css
            )

        if "scrollbar_corner_color" in rules:
            append_declaration(
                "scrollbar-corner-color", self.scrollbar_corner_color.css
            )

        if "scrollbar_background" in rules:
            append_declaration("scrollbar-background", self.scrollbar_background.css)
        if "scrollbar_background_hover" in rules:
            append_declaration(
                "scrollbar-background-hover", self.scrollbar_background_hover.css
            )
        if "scrollbar_background_active" in rules:
            append_declaration(
                "scrollbar-background-active", self.scrollbar_background_active.css
            )

        if "scrollbar_gutter" in rules:
            append_declaration("scrollbar-gutter", self.scrollbar_gutter)
        if "scrollbar_size" in rules:
            append_declaration(
                "scrollbar-size",
                f"{self.scrollbar_size_horizontal} {self.scrollbar_size_vertical}",
            )
        else:
            if "scrollbar_size_horizontal" in rules:
                append_declaration(
                    "scrollbar-size-horizontal", str(self.scrollbar_size_horizontal)
                )
            if "scrollbar_size_vertical" in rules:
                append_declaration(
                    "scrollbar-size-vertical", str(self.scrollbar_size_vertical)
                )

        if "box_sizing" in rules:
            append_declaration("box-sizing", self.box_sizing)
        if "width" in rules:
            append_declaration("width", str(self.width))
        if "height" in rules:
            append_declaration("height", str(self.height))
        if "min_width" in rules:
            append_declaration("min-width", str(self.min_width))
        if "min_height" in rules:
            append_declaration("min-height", str(self.min_height))
        if "max_width" in rules:
            append_declaration("max-width", str(self.min_width))
        if "max_height" in rules:
            append_declaration("max-height", str(self.min_height))
        if "transitions" in rules:
            append_declaration(
                "transition",
                ", ".join(
                    f"{name} {transition}"
                    for name, transition in self.transitions.items()
                ),
            )

        if "align_horizontal" in rules and "align_vertical" in rules:
            append_declaration(
                "align", f"{self.align_horizontal} {self.align_vertical}"
            )
        elif "align_horizontal" in rules:
            append_declaration("align-horizontal", self.align_horizontal)
        elif "align_vertical" in rules:
            append_declaration("align-vertical", self.align_vertical)

        if "content_align_horizontal" in rules and "content_align_vertical" in rules:
            append_declaration(
                "content-align",
                f"{self.content_align_horizontal} {self.content_align_vertical}",
            )
        elif "content_align_horizontal" in rules:
            append_declaration(
                "content-align-horizontal", self.content_align_horizontal
            )
        elif "content_align_vertical" in rules:
            append_declaration("content-align-vertical", self.content_align_vertical)

        if "text_align" in rules:
            append_declaration("text-align", self.text_align)

        if "border_title_align" in rules:
            append_declaration("border-title-align", self.border_title_align)
        if "border_subtitle_align" in rules:
            append_declaration("border-subtitle-align", self.border_subtitle_align)

        if "opacity" in rules:
            append_declaration("opacity", str(self.opacity))
        if "text_opacity" in rules:
            append_declaration("text-opacity", str(self.text_opacity))

        if "grid_columns" in rules:
            append_declaration(
                "grid-columns",
                " ".join(str(scalar) for scalar in self.grid_columns or ()),
            )
        if "grid_rows" in rules:
            append_declaration(
                "grid-rows",
                " ".join(str(scalar) for scalar in self.grid_rows or ()),
            )
        if "grid_size_columns" in rules:
            append_declaration("grid-size-columns", str(self.grid_size_columns))
        if "grid_size_rows" in rules:
            append_declaration("grid-size-rows", str(self.grid_size_rows))

        if "grid_gutter_horizontal" in rules:
            append_declaration(
                "grid-gutter-horizontal", str(self.grid_gutter_horizontal)
            )
        if "grid_gutter_vertical" in rules:
            append_declaration("grid-gutter-vertical", str(self.grid_gutter_vertical))

        if "row_span" in rules:
            append_declaration("row-span", str(self.row_span))
        if "column_span" in rules:
            append_declaration("column-span", str(self.column_span))

        if "link_color" in rules:
            append_declaration("link-color", self.link_color.css)
        if "link_background" in rules:
            append_declaration("link-background", self.link_background.css)
        if "link_style" in rules:
            append_declaration("link-style", str(self.link_style))

        if "link_color_hover" in rules:
            append_declaration("link-color-hover", self.link_color_hover.css)
        if "link_background_hover" in rules:
            append_declaration("link-background-hover", self.link_background_hover.css)
        if "link_style_hover" in rules:
            append_declaration("link-style-hover", str(self.link_style_hover))

        if "border_title_color" in rules:
            append_declaration("title-color", self.border_title_color.css)
        if "border_title_background" in rules:
            append_declaration("title-background", self.border_title_background.css)
        if "border_title_style" in rules:
            append_declaration("title-text-style", str(self.border_title_style))

        if "border_subtitle_color" in rules:
            append_declaration("subtitle-color", self.border_subtitle_color.css)
        if "border_subtitle_background" in rules:
            append_declaration(
                "subtitle-background", self.border_subtitle_background.css
            )
        if "border_subtitle_text_style" in rules:
            append_declaration("subtitle-text-style", str(self.border_subtitle_style))
        if "overlay" in rules:
            append_declaration("overlay", str(self.overlay))
        if "constrain" in rules:
            append_declaration("constrain", str(self.constrain))
        if "keyline" in rules:
            keyline_type, keyline_color = self.keyline
            if keyline_type != "none":
                append_declaration("keyline", f"{keyline_type}, {keyline_color.css}")
        lines.sort()
        return lines

    @property
    def css(self) -> str:
        return "\n".join(self.css_lines)


@rich.repr.auto
class RenderStyles(StylesBase):
    """Presents a combined view of two Styles object: a base Styles and inline Styles."""

    def __init__(self, node: DOMNode, base: Styles, inline_styles: Styles) -> None:
        self.node = node
        self._base_styles = base
        self._inline_styles = inline_styles
        self._animate: BoundAnimator | None = None
        self._updates: int = 0
        self._rich_style: tuple[int, Style] | None = None
        self._gutter: tuple[int, Spacing] | None = None

    def __eq__(self, other: object) -> bool:
        if isinstance(other, RenderStyles):
            return (
                self._base_styles._rules == other._base_styles._rules
                and self._inline_styles._rules == other._inline_styles._rules
            )
        return NotImplemented

    @property
    def _cache_key(self) -> int:
        """A cache key, that changes when any style is changed.

        Returns:
            An opaque integer.
        """
        return self._updates + self._base_styles._updates + self._inline_styles._updates

    @property
    def base(self) -> Styles:
        """Quick access to base (css) style."""
        return self._base_styles

    @property
    def inline(self) -> Styles:
        """Quick access to the inline styles."""
        return self._inline_styles

    @property
    def rich_style(self) -> Style:
        """Get a Rich style for this Styles object."""
        assert self.node is not None
        return self.node.rich_style

    @property
    def gutter(self) -> Spacing:
        """Get space around widget.

        Returns:
            Space around widget content.
        """
        # This is (surprisingly) a bit of a bottleneck
        if self._gutter is not None:
            cache_key, gutter = self._gutter
            if cache_key == self._cache_key:
                return gutter
        gutter = self.padding + self.border.spacing
        self._gutter = (self._cache_key, gutter)
        return gutter

    def animate(
        self,
        attribute: str,
        value: str | float | Animatable,
        *,
        final_value: object = ...,
        duration: float | None = None,
        speed: float | None = None,
        delay: float = 0.0,
        easing: EasingFunction | str = DEFAULT_EASING,
        on_complete: CallbackType | None = None,
        level: AnimationLevel = "full",
    ) -> None:
        """Animate an attribute.

        Args:
            attribute: Name of the attribute to animate.
            value: The value to animate to.
            final_value: The final value of the animation. Defaults to `value` if not set.
            duration: The duration (in seconds) of the animation.
            speed: The speed of the animation.
            delay: A delay (in seconds) before the animation starts.
            easing: An easing method.
            on_complete: A callable to invoke when the animation is finished.
            level: Minimum level required for the animation to take place (inclusive).
        """
        if self._animate is None:
            assert self.node is not None
            self._animate = self.node.app.animator.bind(self)
        assert self._animate is not None
        self._animate(
            attribute,
            value,
            final_value=final_value,
            duration=duration,
            speed=speed,
            delay=delay,
            easing=easing,
            on_complete=on_complete,
            level=level,
        )

    def __rich_repr__(self) -> rich.repr.Result:
        for rule_name in RULE_NAMES:
            if self.has_rule(rule_name):
                yield rule_name, getattr(self, rule_name)

    def refresh(
        self, *, layout: bool = False, children: bool = False, parent: bool = False
    ) -> None:
        self._inline_styles.refresh(layout=layout, children=children, parent=parent)

    def merge(self, other: StylesBase) -> None:
        """Merge values from another Styles.

        Args:
            other: A Styles object.
        """
        self._inline_styles.merge(other)

    def merge_rules(self, rules: RulesMap) -> None:
        self._inline_styles.merge_rules(rules)
        self._updates += 1

    def reset(self) -> None:
        """Reset the rules to initial state."""
        self._inline_styles.reset()
        self._updates += 1

    def has_rule(self, rule: str) -> bool:
        """Check if a rule has been set."""
        return self._inline_styles.has_rule(rule) or self._base_styles.has_rule(rule)

    def set_rule(self, rule: str, value: object | None) -> bool:
        self._updates += 1
        return self._inline_styles.set_rule(rule, value)

    def get_rule(self, rule: str, default: object = None) -> object:
        if self._inline_styles.has_rule(rule):
            return self._inline_styles.get_rule(rule, default)
        return self._base_styles.get_rule(rule, default)

    def clear_rule(self, rule_name: str) -> bool:
        """Clear a rule (from inline)."""
        self._updates += 1
        return self._inline_styles.clear_rule(rule_name)

    def get_rules(self) -> RulesMap:
        """Get rules as a dictionary"""
        rules = {**self._base_styles._rules, **self._inline_styles._rules}
        return cast(RulesMap, rules)

    @property
    def css(self) -> str:
        """Get the CSS for the combined styles."""
        styles = Styles()
        styles.merge(self._base_styles)
        styles.merge(self._inline_styles)
        combined_css = styles.css
        return combined_css
