from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from functools import lru_cache
from operator import attrgetter
from typing import TYPE_CHECKING, Any, Iterable, NamedTuple, cast

import rich.repr
from rich.style import Style

from .._types import CallbackType
from .._animator import BoundAnimator, DEFAULT_EASING, Animatable, EasingFunction
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
    LayoutProperty,
    NameListProperty,
    NameProperty,
    OffsetProperty,
    ScalarListProperty,
    ScalarProperty,
    SpacingProperty,
    StringEnumProperty,
    StyleFlagsProperty,
    TransitionsProperty,
)
from .constants import (
    VALID_ALIGN_HORIZONTAL,
    VALID_ALIGN_VERTICAL,
    VALID_BOX_SIZING,
    VALID_DISPLAY,
    VALID_OVERFLOW,
    VALID_SCROLLBAR_GUTTER,
    VALID_VISIBILITY,
    VALID_TEXT_ALIGN,
)
from .scalar import Scalar, ScalarOffset, Unit
from .scalar_animation import ScalarAnimation
from .transition import Transition
from .types import (
    AlignHorizontal,
    AlignVertical,
    BoxSizing,
    Display,
    Edge,
    Overflow,
    ScrollbarGutter,
    Specificity3,
    Specificity6,
    Visibility,
    TextAlign,
)
from .._typing import TypedDict

if TYPE_CHECKING:
    from .._layout import Layout
    from ..dom import DOMNode


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

    outline_top: tuple[str, Color]
    outline_right: tuple[str, Color]
    outline_bottom: tuple[str, Color]
    outline_left: tuple[str, Color]

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

    link_hover_color: Color
    auto_link_hover_color: bool
    link_hover_background: Color
    link_hover_style: Style


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
        "link_hover_color",
        "link_hover_background",
    }

    node: DOMNode | None = None

    display = StringEnumProperty(VALID_DISPLAY, "block", layout=True)
    visibility = StringEnumProperty(VALID_VISIBILITY, "visible")
    layout = LayoutProperty()

    auto_color = BooleanProperty(default=False)
    color = ColorProperty(Color(255, 255, 255))
    background = ColorProperty(Color(0, 0, 0, 0), background=True)
    text_style = StyleFlagsProperty()

    opacity = FractionalProperty()
    text_opacity = FractionalProperty()

    padding = SpacingProperty()
    margin = SpacingProperty()
    offset = OffsetProperty()

    border = BorderProperty(layout=True)
    border_top = BoxProperty(Color(0, 255, 0))
    border_right = BoxProperty(Color(0, 255, 0))
    border_bottom = BoxProperty(Color(0, 255, 0))
    border_left = BoxProperty(Color(0, 255, 0))

    outline = BorderProperty(layout=False)
    outline_top = BoxProperty(Color(0, 255, 0))
    outline_right = BoxProperty(Color(0, 255, 0))
    outline_bottom = BoxProperty(Color(0, 255, 0))
    outline_left = BoxProperty(Color(0, 255, 0))

    box_sizing = StringEnumProperty(VALID_BOX_SIZING, "border-box", layout=True)
    width = ScalarProperty(percent_unit=Unit.WIDTH)
    height = ScalarProperty(percent_unit=Unit.HEIGHT)
    min_width = ScalarProperty(percent_unit=Unit.WIDTH, allow_auto=False)
    min_height = ScalarProperty(percent_unit=Unit.HEIGHT, allow_auto=False)
    max_width = ScalarProperty(percent_unit=Unit.WIDTH, allow_auto=False)
    max_height = ScalarProperty(percent_unit=Unit.HEIGHT, allow_auto=False)

    dock = DockProperty()

    overflow_x = StringEnumProperty(VALID_OVERFLOW, "hidden")
    overflow_y = StringEnumProperty(VALID_OVERFLOW, "hidden")

    layer = NameProperty()
    layers = NameListProperty()
    transitions = TransitionsProperty()

    tint = ColorProperty("transparent")
    scrollbar_color = ColorProperty("ansi_bright_magenta")
    scrollbar_color_hover = ColorProperty("ansi_yellow")
    scrollbar_color_active = ColorProperty("ansi_bright_yellow")

    scrollbar_corner_color = ColorProperty("#666666")

    scrollbar_background = ColorProperty("#555555")
    scrollbar_background_hover = ColorProperty("#444444")
    scrollbar_background_active = ColorProperty("black")

    scrollbar_gutter = StringEnumProperty(VALID_SCROLLBAR_GUTTER, "auto")

    scrollbar_size_vertical = IntegerProperty(default=1, layout=True)
    scrollbar_size_horizontal = IntegerProperty(default=1, layout=True)

    align_horizontal = StringEnumProperty(VALID_ALIGN_HORIZONTAL, "left")
    align_vertical = StringEnumProperty(VALID_ALIGN_VERTICAL, "top")
    align = AlignProperty()

    content_align_horizontal = StringEnumProperty(VALID_ALIGN_HORIZONTAL, "left")
    content_align_vertical = StringEnumProperty(VALID_ALIGN_VERTICAL, "top")
    content_align = AlignProperty()

    grid_rows = ScalarListProperty()
    grid_columns = ScalarListProperty()

    grid_size_columns = IntegerProperty(default=1, layout=True)
    grid_size_rows = IntegerProperty(default=0, layout=True)
    grid_gutter_horizontal = IntegerProperty(default=0, layout=True)
    grid_gutter_vertical = IntegerProperty(default=0, layout=True)

    row_span = IntegerProperty(default=1, layout=True)
    column_span = IntegerProperty(default=1, layout=True)

    text_align = StringEnumProperty(VALID_TEXT_ALIGN, "start")

    link_color = ColorProperty("transparent")
    auto_link_color = BooleanProperty(False)
    link_background = ColorProperty("transparent")
    link_style = StyleFlagsProperty()

    link_hover_color = ColorProperty("transparent")
    auto_link_hover_color = BooleanProperty(False)
    link_hover_background = ColorProperty("transparent")
    link_hover_style = StyleFlagsProperty()

    def __eq__(self, styles: object) -> bool:
        """Check that Styles contains the same rules."""
        if not isinstance(styles, StylesBase):
            return NotImplemented
        return self.get_rules() == styles.get_rules()

    @property
    def gutter(self) -> Spacing:
        """Get space around widget.

        Returns:
            Spacing: Space around widget content.
        """
        spacing = self.padding + self.border.spacing
        return spacing

    @property
    def auto_dimensions(self) -> bool:
        """Check if width or height are set to 'auto'."""
        has_rule = self.has_rule
        return (has_rule("width") and self.width.is_auto) or (
            has_rule("height") and self.height.is_auto
        )

    @abstractmethod
    def has_rule(self, rule: str) -> bool:
        """Check if a rule is set on this Styles object.

        Args:
            rule (str): Rule name.

        Returns:
            bool: ``True`` if the rules is present, otherwise ``False``.
        """

    @abstractmethod
    def clear_rule(self, rule: str) -> bool:
        """Removes the rule from the Styles object, as if it had never been set.

        Args:
            rule (str): Rule name.

        Returns:
            bool: ``True`` if a rule was cleared, or ``False`` if the rule is already not set.
        """

    @abstractmethod
    def get_rules(self) -> RulesMap:
        """Get the rules in a mapping.

        Returns:
            RulesMap: A TypedDict of the rules.
        """

    @abstractmethod
    def set_rule(self, rule: str, value: object | None) -> bool:
        """Set a rule.

        Args:
            rule (str): Rule name.
            value (object | None): New rule value.

        Returns:
            bool: ``True`` if the rule changed, otherwise ``False``.
        """

    @abstractmethod
    def get_rule(self, rule: str, default: object = None) -> object:
        """Get an individual rule.

        Args:
            rule (str): Name of rule.
            default (object, optional): Default if rule does not exists. Defaults to None.

        Returns:
            object: Rule value or default.
        """

    @abstractmethod
    def refresh(self, *, layout: bool = False, children: bool = False) -> None:
        """Mark the styles as requiring a refresh.

        Args:
            layout (bool, optional): Also require a layout. Defaults to False.
            children (bool, opional): Also refresh children. Defaults to False.
        """

    @abstractmethod
    def reset(self) -> None:
        """Reset the rules to initial state."""

    @abstractmethod
    def merge(self, other: StylesBase) -> None:
        """Merge values from another Styles.

        Args:
            other (Styles): A Styles object.
        """

    @abstractmethod
    def merge_rules(self, rules: RulesMap) -> None:
        """Merge rules in to Styles.

        Args:
            rules (RulesMap): A mapping of rules.
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
            rule (str): Name of the rule.

        Returns:
            bool: ``True`` if the rule may be animated, otherwise ``False``.
        """
        return rule in cls.ANIMATABLE

    @classmethod
    @lru_cache(maxsize=1024)
    def parse(cls, css: str, path: str, *, node: DOMNode = None) -> Styles:
        """Parse CSS and return a Styles object.

        Args:
            css (str): Textual CSS.
            path (str): Path or string indicating source of CSS.
            node (DOMNode, optional): Node to associate with the Styles. Defaults to None.

        Returns:
            Styles: A Styles instance containing result of parsing CSS.
        """
        from .parse import parse_declarations

        styles = parse_declarations(css, path)
        styles.node = node
        return styles

    def _get_transition(self, key: str) -> Transition | None:
        """Get a transition.

        Args:
            key (str): Transition key.

        Returns:
            Transition | None: Transition object or None it no transition exists.
        """
        if key in self.ANIMATABLE:
            return self.transitions.get(key, None)
        else:
            return None

    def _align_width(self, width: int, parent_width: int) -> int:
        """Align the width dimension.

        Args:
            width (int): Width of the content.
            parent_width (int): Width of the parent container.

        Returns:
            int: An offset to add to the X coordinate.
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
            height (int): Height of the content.
            parent_height (int): Height of the parent container.

        Returns:
            int: An offset to add to the Y coordinate.
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
            child (tuple[int, int]): The size of the child (width, height)
            parent (tuple[int, int]): The size of the parent (width, height)

        Returns:
            Offset: Offset required to align the child.
        """
        width, height = child
        parent_width, parent_height = parent
        return Offset(
            self._align_width(width, parent_width),
            self._align_height(height, parent_height),
        )


@rich.repr.auto
@dataclass
class Styles(StylesBase):
    node: DOMNode | None = None
    _rules: RulesMap = field(default_factory=dict)

    important: set[str] = field(default_factory=set)

    def copy(self) -> Styles:
        """Get a copy of this Styles object."""
        return Styles(node=self.node, _rules=self.get_rules(), important=self.important)

    def has_rule(self, rule: str) -> bool:
        assert rule in RULE_NAMES_SET, f"no such rule {rule!r}"
        return rule in self._rules

    def clear_rule(self, rule: str) -> bool:
        """Removes the rule from the Styles object, as if it had never been set.

        Args:
            rule (str): Rule name.

        Returns:
            bool: ``True`` if a rule was cleared, or ``False`` if it was already not set.
        """
        return self._rules.pop(rule, None) is not None

    def get_rules(self) -> RulesMap:
        return self._rules.copy()

    def set_rule(self, rule: str, value: object | None) -> bool:
        """Set a rule.

        Args:
            rule (str): Rule name.
            value (object | None): New rule value.

        Returns:
            bool: ``True`` if the rule changed, otherwise ``False``.
        """
        if value is None:
            return self._rules.pop(rule, None) is not None
        else:
            current = self._rules.get(rule)
            self._rules[rule] = value
            return current != value

    def get_rule(self, rule: str, default: object = None) -> object:
        return self._rules.get(rule, default)

    def refresh(self, *, layout: bool = False, children: bool = False) -> None:
        if self.node is not None:
            self.node.refresh(layout=layout)
            if children:
                for child in self.node.walk_children(with_self=False, reverse=True):
                    child.refresh(layout=layout)

    def reset(self) -> None:
        """Reset the rules to initial state."""
        self._rules.clear()

    def merge(self, other: Styles) -> None:
        """Merge values from another Styles.

        Args:
            other (Styles): A Styles object.
        """

        self._rules.update(other._rules)

    def merge_rules(self, rules: RulesMap) -> None:
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
            specificity (Specificity3): A node specificity.
            is_default_rules (bool): True if the rules we're extracting are
                default (i.e. in Widget.DEFAULT_CSS) rules. False if they're from user defined CSS.

        Returns:
            list[tuple[str, Specificity6, Any]]]: A list containing a tuple of <RULE NAME>, <SPECIFICITY> <RULE VALUE>.
        """
        is_important = self.important.__contains__
        rules = [
            (
                rule_name,
                (
                    0 if is_default_rules else 1,
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

    def __textual_animation__(
        self,
        attribute: str,
        value: Any,
        start_time: float,
        duration: float | None,
        speed: float | None,
        easing: EasingFunction,
        on_complete: CallbackType | None = None,
    ) -> ScalarAnimation | None:
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
                on_complete=on_complete,
            )
        return None

    def _get_border_css_lines(
        self, rules: RulesMap, name: str
    ) -> Iterable[tuple[str, str]]:
        """Get pairs of strings containing <RULE NAME>, <RULE VALUE> for border css declarations.

        Args:
            rules (RulesMap): A rules map.
            name (str): Name of rules (border or outline)

        Returns:
            Iterable[tuple[str, str]]: An iterable of CSS declarations.

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
                border_type, border_color = rules[f"{name}_top"]
                yield name, f"{border_type} {border_color.hex}"
                return

        # Check for edges
        if has_top:
            border_type, border_color = rules[f"{name}_top"]
            yield f"{name}-top", f"{border_type} {border_color.hex}"

        if has_right:
            border_type, border_color = rules[f"{name}_right"]
            yield f"{name}-right", f"{border_type} {border_color.hex}"

        if has_bottom:
            border_type, border_color = rules[f"{name}_bottom"]
            yield f"{name}-bottom", f"{border_type} {border_color.hex}"

        if has_left:
            border_type, border_color = rules[f"{name}_left"]
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
        has_rule = rules.__contains__

        if has_rule("display"):
            append_declaration("display", rules["display"])
        if has_rule("visibility"):
            append_declaration("visibility", rules["visibility"])
        if has_rule("padding"):
            append_declaration("padding", rules["padding"].css)
        if has_rule("margin"):
            append_declaration("margin", rules["margin"].css)

        for name, rule in self._get_border_css_lines(rules, "border"):
            append_declaration(name, rule)

        for name, rule in self._get_border_css_lines(rules, "outline"):
            append_declaration(name, rule)

        if has_rule("offset"):
            x, y = self.offset
            append_declaration("offset", f"{x} {y}")
        if has_rule("dock"):
            append_declaration("dock", rules["dock"])
        if has_rule("layers"):
            append_declaration("layers", " ".join(self.layers))
        if has_rule("layer"):
            append_declaration("layer", self.layer)
        if has_rule("layout"):
            assert self.layout is not None
            append_declaration("layout", self.layout.name)

        if has_rule("color"):
            append_declaration("color", self.color.hex)
        if has_rule("background"):
            append_declaration("background", self.background.hex)
        if has_rule("text_style"):
            append_declaration("text-style", str(get_rule("text_style")))
        if has_rule("tint"):
            append_declaration("tint", self.tint.css)

        if has_rule("overflow_x"):
            append_declaration("overflow-x", self.overflow_x)
        if has_rule("overflow_y"):
            append_declaration("overflow-y", self.overflow_y)

        if has_rule("scrollbar_color"):
            append_declaration("scrollbar-color", self.scrollbar_color.css)
        if has_rule("scrollbar_color_hover"):
            append_declaration("scrollbar-color-hover", self.scrollbar_color_hover.css)
        if has_rule("scrollbar_color_active"):
            append_declaration(
                "scrollbar-color-active", self.scrollbar_color_active.css
            )

        if has_rule("scrollbar_corner_color"):
            append_declaration(
                "scrollbar-corner-color", self.scrollbar_corner_color.css
            )

        if has_rule("scrollbar_background"):
            append_declaration("scrollbar-background", self.scrollbar_background.css)
        if has_rule("scrollbar_background_hover"):
            append_declaration(
                "scrollbar-background-hover", self.scrollbar_background_hover.css
            )
        if has_rule("scrollbar_background_active"):
            append_declaration(
                "scrollbar-background-active", self.scrollbar_background_active.css
            )

        if has_rule("scrollbar_gutter"):
            append_declaration("scrollbar-gutter", self.scrollbar_gutter)
        if has_rule("scrollbar_size"):
            append_declaration(
                "scrollbar-size",
                f"{self.scrollbar_size_horizontal} {self.scrollbar_size_vertical}",
            )
        else:
            if has_rule("scrollbar_size_horizontal"):
                append_declaration(
                    "scrollbar-size-horizontal", str(self.scrollbar_size_horizontal)
                )
            if has_rule("scrollbar_size_vertical"):
                append_declaration(
                    "scrollbar-size-vertical", str(self.scrollbar_size_vertical)
                )

        if has_rule("box_sizing"):
            append_declaration("box-sizing", self.box_sizing)
        if has_rule("width"):
            append_declaration("width", str(self.width))
        if has_rule("height"):
            append_declaration("height", str(self.height))
        if has_rule("min_width"):
            append_declaration("min-width", str(self.min_width))
        if has_rule("min_height"):
            append_declaration("min-height", str(self.min_height))
        if has_rule("max_width"):
            append_declaration("max-width", str(self.min_width))
        if has_rule("max_height"):
            append_declaration("max-height", str(self.min_height))
        if has_rule("transitions"):
            append_declaration(
                "transition",
                ", ".join(
                    f"{name} {transition}"
                    for name, transition in self.transitions.items()
                ),
            )

        if has_rule("align_horizontal") and has_rule("align_vertical"):
            append_declaration(
                "align", f"{self.align_horizontal} {self.align_vertical}"
            )
        elif has_rule("align_horizontal"):
            append_declaration("align-horizontal", self.align_horizontal)
        elif has_rule("align_vertical"):
            append_declaration("align-vertical", self.align_vertical)

        if has_rule("content_align_horizontal") and has_rule("content_align_vertical"):
            append_declaration(
                "content-align",
                f"{self.content_align_horizontal} {self.content_align_vertical}",
            )
        elif has_rule("content_align_horizontal"):
            append_declaration(
                "content-align-horizontal", self.content_align_horizontal
            )
        elif has_rule("content_align_vertical"):
            append_declaration("content-align-vertical", self.content_align_vertical)

        if has_rule("text_align"):
            append_declaration("text-align", self.text_align)

        if has_rule("opacity"):
            append_declaration("opacity", str(self.opacity))
        if has_rule("text_opacity"):
            append_declaration("text-opacity", str(self.text_opacity))

        if has_rule("grid_columns"):
            append_declaration(
                "grid-columns",
                " ".join(str(scalar) for scalar in self.grid_columns or ()),
            )
        if has_rule("grid_rows"):
            append_declaration(
                "grid-rows",
                " ".join(str(scalar) for scalar in self.grid_rows or ()),
            )
        if has_rule("grid_size_columns"):
            append_declaration("grid-size-columns", str(self.grid_size_columns))
        if has_rule("grid_size_rows"):
            append_declaration("grid-size-rows", str(self.grid_size_rows))

        if has_rule("grid_gutter_horizontal"):
            append_declaration(
                "grid-gutter-horizontal", str(self.grid_gutter_horizontal)
            )
        if has_rule("grid_gutter_vertical"):
            append_declaration("grid-gutter-vertical", str(self.grid_gutter_vertical))

        if has_rule("row_span"):
            append_declaration("row-span", str(self.row_span))
        if has_rule("column_span"):
            append_declaration("column-span", str(self.column_span))

        if has_rule("link_color"):
            append_declaration("link-color", self.link_color.css)
        if has_rule("link_background"):
            append_declaration("link-background", self.link_background.css)
        if has_rule("link_style"):
            append_declaration("link-style", str(self.link_style))

        if has_rule("link_hover_color"):
            append_declaration("link-hover-color", self.link_hover_color.css)
        if has_rule("link_hover_background"):
            append_declaration("link-hover-background", self.link_hover_background.css)
        if has_rule("link_hover_style"):
            append_declaration("link-hover-style", str(self.link_hover_style))

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

    def animate(
        self,
        attribute: str,
        value: float | Animatable,
        *,
        final_value: object = ...,
        duration: float | None = None,
        speed: float | None = None,
        delay: float = 0.0,
        easing: EasingFunction | str = DEFAULT_EASING,
        on_complete: CallbackType | None = None,
    ) -> None:
        """Animate an attribute.

        Args:
            attribute (str): Name of the attribute to animate.
            value (float | Animatable): The value to animate to.
            final_value (object, optional): The final value of the animation. Defaults to `value` if not set.
            duration (float | None, optional): The duration of the animate. Defaults to None.
            speed (float | None, optional): The speed of the animation. Defaults to None.
            delay (float, optional): A delay (in seconds) before the animation starts. Defaults to 0.0.
            easing (EasingFunction | str, optional): An easing method. Defaults to "in_out_cubic".
            on_complete (CallbackType | None, optional): A callable to invoke when the animation is finished. Defaults to None.

        """
        if self._animate is None:
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
        )

    def __rich_repr__(self) -> rich.repr.Result:
        for rule_name in RULE_NAMES:
            if self.has_rule(rule_name):
                yield rule_name, getattr(self, rule_name)

    def refresh(self, *, layout: bool = False, children: bool = False) -> None:
        self._inline_styles.refresh(layout=layout, children=children)

    def merge(self, other: Styles) -> None:
        """Merge values from another Styles.

        Args:
            other (Styles): A Styles object.
        """
        self._inline_styles.merge(other)

    def merge_rules(self, rules: RulesMap) -> None:
        self._inline_styles.merge_rules(rules)

    def reset(self) -> None:
        """Reset the rules to initial state."""
        self._inline_styles.reset()

    def has_rule(self, rule: str) -> bool:
        """Check if a rule has been set."""
        return self._inline_styles.has_rule(rule) or self._base_styles.has_rule(rule)

    def set_rule(self, rule: str, value: object | None) -> bool:
        return self._inline_styles.set_rule(rule, value)

    def get_rule(self, rule: str, default: object = None) -> object:
        if self._inline_styles.has_rule(rule):
            return self._inline_styles.get_rule(rule, default)
        return self._base_styles.get_rule(rule, default)

    def clear_rule(self, rule_name: str) -> bool:
        """Clear a rule (from inline)."""
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


if __name__ == "__main__":
    styles = Styles()

    styles.display = "none"
    styles.visibility = "hidden"
    styles.border = ("solid", "rgb(10,20,30)")
    styles.outline_right = ("solid", "red")
    styles.text_style = "italic"
    styles.dock = "bar"
    styles.layers = "foo bar"

    from rich import print

    print(styles.text_style)
    print(styles.text)

    print(styles)
    print(styles.css)

    print(styles.extract_rules((0, 1, 0)))
