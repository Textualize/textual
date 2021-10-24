from __future__ import annotations

from dataclasses import dataclass, field

from rich import print
import rich.repr
from rich.color import Color
from rich.style import Style

from .errors import StyleValueError
from ._error_tools import friendly_list
from .constants import (
    VALID_DISPLAY,
    VALID_VISIBILITY,
    VALID_EDGE,
    VALID_LAYOUT,
    NULL_SPACING,
)
from ..geometry import NULL_OFFSET, Offset, Spacing
from ._style_properties import (
    _BorderProperty,
    _BoxProperty,
    _DocksProperty,
    _DockGroupProperty,
    _OffsetProperty,
    _SpacingProperty,
    _StyleProperty,
)
from .types import Display, Visibility


@dataclass
class Styles:

    _display: Display | None = None
    _visibility: Visibility | None = None

    _text: Style = Style()

    _layout: str = ""
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

    _dock_group: str | None = None
    _dock_edge: str = ""
    _docks: tuple[str, ...] | None = None

    important: set[str] = field(default_factory=set)

    @property
    def display(self) -> Display:
        return self._display or "block"

    @display.setter
    def display(self, display: Display) -> None:
        if display not in VALID_DISPLAY:
            raise StyleValueError(
                f"display must be one of {friendly_list(VALID_DISPLAY)}"
            )
        self._display = display

    @property
    def visibility(self) -> Visibility:
        return self._visibility or "visible"

    @visibility.setter
    def visibility(self, visibility: Visibility) -> None:
        if visibility not in VALID_VISIBILITY:
            raise StyleValueError(
                f"visibility must be one of {friendly_list(VALID_VISIBILITY)}"
            )
        self._visibility = visibility

    text = _StyleProperty()

    @property
    def layout(self) -> str:
        return self._layout

    @layout.setter
    def layout(self, layout: str) -> None:
        if layout not in VALID_LAYOUT:
            raise StyleValueError(
                f"layout must be one of {friendly_list(VALID_LAYOUT)}"
            )
        self._layout = layout

    offset = _OffsetProperty()

    padding = _SpacingProperty()
    margin = _SpacingProperty()

    border = _BorderProperty()
    outline = _BorderProperty()

    border_top = _BoxProperty()
    border_right = _BoxProperty()
    border_bottom = _BoxProperty()
    border_left = _BoxProperty()

    outline_top = _BoxProperty()
    outline_right = _BoxProperty()
    outline_bottom = _BoxProperty()
    outline_left = _BoxProperty()

    dock_group = _DockGroupProperty()
    docks = _DocksProperty()

    @property
    def dock_edge(self) -> str:
        return self._dock_edge

    @dock_edge.setter
    def dock_edge(self, edge: str) -> str:
        if edge not in VALID_EDGE:
            raise ValueError(f"dock edge must be one of {friendly_list(VALID_EDGE)}")
        self._dock_edge = edge
        return edge

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

    # print(styles)
    # print(styles.outline)

    # inspect(styles)
