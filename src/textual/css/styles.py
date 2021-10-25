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
    SpacingProperty,
    StringProperty,
    StyleProperty,
)
from .types import Display, Visibility


@dataclass
class Styles:

    _display: Display | None = None
    _visibility: Visibility | None = None
    _layout: str | None = None

    _text: Style | None = None

    _padding: Spacing | None = None
    _margin: Spacing | None = None
    _offset: Offset | None = None

    _border_top: tuple[str, Style] | None = None
    _border_right: tuple[str, Style] | None = None
    _border_bottom: tuple[str, Style] | None = None
    _border_left: tuple[str, Style] | None = None

    _outline_top: tuple[str, Style] | None = None
    _outline_right: tuple[str, Style] | None = None
    _outline_bottom: tuple[str, Style] | None = None
    _outline_left: tuple[str, Style] | None = None

    _size: int | None = None
    _fraction: int | None = None
    _min_size: int | None = None

    _dock_group: str | None = None
    _dock_edge: str | None = None
    _docks: tuple[str, ...] | None = None

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

    @property
    def has_border(self) -> bool:
        """Check in a border is present."""
        return any(edge for edge, _style in self.border)

    @property
    def has_outline(self) -> bool:
        """Check if an outline is present."""
        return any(edge for edge, _style in self.outline)

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

        if self._display is not None:
            append_declaration("display", self._display)
        if self._visibility is not None:
            append_declaration("visibility", self._visibility)
        if self._text is not None:
            append_declaration("text", str(self._text))
        if self._padding is not None:
            append_declaration("padding", self._padding.packed)
        if self._margin is not None:
            append_declaration("margin", self._margin.packed)

        if (
            self._border_top is not None
            and self._border_top == self._border_right
            and self._border_right == self._border_bottom
            and self._border_bottom == self._border_left
        ):
            _type, style = self._border_top
            append_declaration("border", f"{_type} {style}")
        else:
            if self._border_top is not None:
                _type, style = self._border_top
                append_declaration("border-top", f"{_type} {style}")
            if self._border_right is not None:
                _type, style = self._border_right
                append_declaration("border-right", f"{_type} {style}")
            if self._border_bottom is not None:
                _type, style = self._border_bottom
                append_declaration("border-bottom", f"{_type} {style}")
            if self._border_left is not None:
                _type, style = self._border_left
                append_declaration("border-left", f"{_type} {style}")

        if (
            self._outline_top is not None
            and self._outline_top == self._outline_right
            and self._outline_right == self._outline_bottom
            and self._outline_bottom == self._outline_left
        ):
            _type, style = self._outline_top
            append_declaration("outline", f"{_type} {style}")
        else:
            if self._outline_top is not None:
                _type, style = self._outline_top
                append_declaration("outline-top", f"{_type} {style}")
            if self._outline_right is not None:
                _type, style = self._outline_right
                append_declaration("outline-right", f"{_type} {style}")
            if self._outline_bottom is not None:
                _type, style = self._outline_bottom
                append_declaration("outline-bottom", f"{_type} {style}")
            if self._outline_left is not None:
                _type, style = self._outline_left
                append_declaration("outline-left", f"{_type} {style}")

        if self.offset:
            x, y = self.offset
            append_declaration("offset", f"{x} {y}")
        if self._dock_group:
            append_declaration("dock-group", self._dock_group)
        if self._docks:
            append_declaration("docks", " ".join(self._docks))
        if self._dock_edge:
            append_declaration("dock-edge", self._dock_edge)
        lines.sort()
        return lines

    @property
    def css(self) -> str:
        return "\n".join(self.css_lines)


if __name__ == "__main__":
    styles = Styles()

    styles.display = "none"
    styles.visibility = "hidden"
    styles.border = ("solid", "rgb(10,20,30)")
    styles.outline_right = ("solid", "red")
    styles.docks = "foo bar"
    styles.text = "italic blue"
    styles.dock_group = "bar"

    from rich import inspect, print

    print(styles)
    print(styles.css)
