from __future__ import annotations

from typing import Iterable, NamedTuple, Sequence, TYPE_CHECKING

import rich.repr
from rich.color import Color
from rich.style import Style

from .scalar import Scalar, ScalarParseError
from ..geometry import Offset, Spacing, SpacingDimensions
from .constants import NULL_SPACING, VALID_EDGE
from .errors import StyleTypeError, StyleValueError
from ._error_tools import friendly_list

if TYPE_CHECKING:
    from .styles import Styles


class ScalarProperty:
    def __init__(self, units: set[str]) -> None:
        self.units = units
        super().__init__()

    def __set_name__(self, owner: Styles, name: str) -> None:
        self.internal_name = f"_rule_{name}"

    def __get__(
        self, obj: Styles, objtype: type[Styles] | None = None
    ) -> Scalar | None:
        value = getattr(obj, self.internal_name)
        return value

    def __set__(
        self, obj: Styles, value: float | Scalar | str | None
    ) -> float | Scalar | str | None:
        new_value: Scalar | None = None
        if value is None:
            new_value = None
        elif isinstance(value, float):
            new_value = Scalar(value, "")
        elif isinstance(value, Scalar):
            new_value = value
        elif isinstance(value, str):
            try:
                new_value = Scalar.parse(value)
            except ScalarParseError:
                raise StyleValueError("unable to parse scalar from {value!r}")
        else:
            raise StyleValueError("expected float, Scalar, or None")
        if new_value is not None and new_value.unit not in self.units:
            raise StyleValueError(f"units must be one of {friendly_list(self.units)}")
        setattr(obj, self.internal_name, new_value)
        return value


class BoxProperty:

    DEFAULT = ("", Style())

    def __set_name__(self, owner: Styles, name: str) -> None:
        self.internal_name = f"_rule_{name}"
        _type, edge = name.split("_")
        self._type = _type
        self.edge = edge

    def __get__(
        self, obj: Styles, objtype: type[Styles] | None = None
    ) -> tuple[str, Style]:
        value = getattr(obj, self.internal_name)
        return value or self.DEFAULT

    def __set__(
        self, obj: Styles, border: tuple[str, str | Color | Style] | None
    ) -> tuple[str, str | Color | Style] | None:
        if border is None:
            new_value = None
        else:
            _type, color = border
            if isinstance(color, str):
                new_value = (_type, Style.parse(color))
            elif isinstance(color, Color):
                new_value = (_type, Style.from_color(color))
            else:
                new_value = (_type, Style.from_color(Color.parse(color)))
        setattr(obj, self.internal_name, new_value)
        return border


@rich.repr.auto
class Edges(NamedTuple):
    """Stores edges for border / outline."""

    top: tuple[str, Style]
    right: tuple[str, Style]
    bottom: tuple[str, Style]
    left: tuple[str, Style]

    def __rich_repr__(self) -> rich.repr.Result:
        top, right, bottom, left = self
        if top[0]:
            yield "top", top
        if right[0]:
            yield "right", right
        if bottom[0]:
            yield "bottom", bottom
        if left[0]:
            yield "left", left


class BorderProperty:
    def __set_name__(self, owner: Styles, name: str) -> None:
        self._properties = (
            f"{name}_top",
            f"{name}_right",
            f"{name}_bottom",
            f"{name}_left",
        )

    def __get__(self, obj: Styles, objtype: type[Styles] | None = None) -> Edges:
        top, right, bottom, left = self._properties
        border = Edges(
            getattr(obj, top),
            getattr(obj, right),
            getattr(obj, bottom),
            getattr(obj, left),
        )
        return border

    def __set__(
        self,
        obj: Styles,
        border: Sequence[tuple[str, str | Color | Style] | None]
        | tuple[str, str | Color | Style]
        | None,
    ) -> None:
        top, right, bottom, left = self._properties
        if border is None:
            setattr(obj, top, None)
            setattr(obj, right, None)
            setattr(obj, bottom, None)
            setattr(obj, left, None)
            return
        if isinstance(border, tuple):
            setattr(obj, top, border)
            setattr(obj, right, border)
            setattr(obj, bottom, border)
            setattr(obj, left, border)
            return
        count = len(border)
        if count == 1:
            _border = border[0]
            setattr(obj, top, _border)
            setattr(obj, right, _border)
            setattr(obj, bottom, _border)
            setattr(obj, left, _border)
        elif count == 2:
            _border1, _border2 = border
            setattr(obj, top, _border1)
            setattr(obj, right, _border1)
            setattr(obj, bottom, _border2)
            setattr(obj, left, _border2)
        elif count == 4:
            _border1, _border2, _border3, _border4 = border
            setattr(obj, top, _border1)
            setattr(obj, right, _border2)
            setattr(obj, bottom, _border3)
            setattr(obj, left, _border4)
        else:
            raise StyleValueError("expected 1, 2, or 4 values")


class StyleProperty:

    DEFAULT_STYLE = Style()

    def __set_name__(self, owner: Styles, name: str) -> None:

        self._color_name = f"_rule_{name}_color"
        self._bgcolor_name = f"_rule_{name}_background"
        self._style_name = f"_rule_{name}_style"

    def __get__(self, obj: Styles, objtype: type[Styles] | None = None) -> Style:

        color = getattr(obj, self._color_name)
        bgcolor = getattr(obj, self._bgcolor_name)
        style = Style.from_color(color, bgcolor)
        style_flags = getattr(obj, self._style_name)
        if style_flags is not None:
            style += Style.parse(style_flags)
        return style

    def __set__(self, obj: Styles, style: Style | str | None) -> Style | str | None:
        if style is None:
            setattr(obj, self._color_name, None)
            setattr(obj, self._bgcolor_name, None)
            setattr(obj, self._style_name, None)
        elif isinstance(style, Style):
            setattr(obj, self._color_name, style.color)
            setattr(obj, self._bgcolor_name, style.bgcolor)
            setattr(obj, self._style_name, str(style.without_color))
        elif isinstance(style, str):
            new_style = Style.parse(style)
            setattr(obj, self._color_name, new_style.color)
            setattr(obj, self._bgcolor_name, new_style.bgcolor)
            style_str = str(new_style.without_color)
            setattr(obj, self._style_name, style_str if style_str != "none" else "")
        return style


class SpacingProperty:
    def __set_name__(self, owner: Styles, name: str) -> None:
        self._internal_name = f"_rule_{name}"

    def __get__(self, obj: Styles, objtype: type[Styles] | None = None) -> Spacing:
        return getattr(obj, self._internal_name) or NULL_SPACING

    def __set__(self, obj: Styles, spacing: SpacingDimensions) -> Spacing:
        spacing = Spacing.unpack(spacing)
        setattr(obj, self._internal_name, spacing)
        return spacing


class DocksProperty:
    def __get__(
        self, obj: Styles, objtype: type[Styles] | None = None
    ) -> tuple[tuple[str, str], ...]:
        return obj._rule_docks or ()

    def __set__(
        self, obj: Styles, docks: Iterable[tuple[str, str]] | None
    ) -> Iterable[tuple[str, str]] | None:
        if docks is None:
            obj._rule_docks = docks
        else:
            obj._rule_docks = tuple(docks)
        return docks


class DockGroupProperty:
    def __get__(self, obj: Styles, objtype: type[Styles] | None = None) -> str:
        return obj._rule_dock_group or ""

    def __set__(self, obj: Styles, spacing: str | None) -> str | None:
        obj._rule_dock_group = spacing
        return spacing


class OffsetProperty:
    def __set_name__(self, owner: Styles, name: str) -> None:
        self._internal_name = f"_rule_{name}"

    def __get__(self, obj: Styles, objtype: type[Styles] | None = None) -> Offset:
        return getattr(obj, self._internal_name) or Offset()

    def __set__(self, obj: Styles, offset: tuple[int, int]) -> tuple[int, int]:
        _offset = Offset(*offset)
        setattr(obj, self._internal_name, _offset)
        return offset


class DockEdgeProperty:
    def __get__(self, obj: Styles, objtype: type[Styles] | None = None) -> str:
        return obj._rule_dock_edge or ""

    def __set__(self, obj: Styles, edge: str | None) -> str | None:
        if isinstance(edge, str) and edge not in VALID_EDGE:
            raise ValueError(f"dock edge must be one of {friendly_list(VALID_EDGE)}")
        obj._rule_dock_edge = edge
        return edge


class IntegerProperty:
    def __set_name__(self, owner: Styles, name: str) -> None:
        self._name = name
        self._internal_name = f"_{name}"

    def __get__(self, obj: Styles, objtype: type[Styles] | None = None) -> int:
        return getattr(obj, self._internal_name, 0)

    def __set__(self, obj: Styles, value: int | None) -> int | None:
        if not isinstance(value, int):
            raise StyleTypeError(f"{self._name} must be a str")
        setattr(obj, self._internal_name, value)
        return value


class StringProperty:
    def __init__(self, valid_values: set[str], default: str) -> None:
        self._valid_values = valid_values
        self._default = default

    def __set_name__(self, owner: Styles, name: str) -> None:
        self._name = name
        self._internal_name = f"_rule_{name}"

    def __get__(self, obj: Styles, objtype: type[Styles] | None = None) -> str:
        return getattr(obj, self._internal_name, None) or self._default

    def __set__(self, obj: Styles, value: str | None = None) -> str | None:
        if value is not None:
            if value not in self._valid_values:
                raise StyleValueError(
                    f"{self._name} must be one of {friendly_list(self._valid_values)}"
                )
        setattr(obj, self._internal_name, value)
        return value


class NameProperty:
    def __set_name__(self, owner: Styles, name: str) -> None:
        self._name = name
        self._internal_name = f"_rule_{name}"

    def __get__(self, obj: Styles, objtype: type[Styles] | None) -> str:
        return getattr(obj, self._internal_name, None) or ""

    def __set__(self, obj: Styles, name: str | None) -> str | None:
        if not isinstance(name, str):
            raise StyleTypeError(f"{self._name} must be a str")
        setattr(obj, self._internal_name, name)
        return name


class NameListProperty:
    def __set_name__(self, owner: Styles, name: str) -> None:
        self._name = name
        self._internal_name = f"_rule_{name}"

    def __get__(
        self, obj: Styles, objtype: type[Styles] | None = None
    ) -> tuple[str, ...]:
        return getattr(obj, self._internal_name, None) or ()

    def __set__(
        self, obj: Styles, names: str | tuple[str] | None = None
    ) -> str | tuple[str] | None:
        names_value: tuple[str, ...] | None = None
        if isinstance(names, str):
            names_value = tuple(name.strip().lower() for name in names.split(" "))
        elif isinstance(names, tuple):
            names_value = names
        elif names is None:
            names_value = None
        setattr(obj, self._internal_name, names_value)
        return names


class ColorProperty:
    def __set_name__(self, owner: Styles, name: str) -> None:
        self._name = name
        self._internal_name = f"_rule_{name}"

    def __get__(self, obj: Styles, objtype: type[Styles] | None = None) -> Color:
        return getattr(obj, self._internal_name, None) or Color.default()

    def __set__(self, obj: Styles, color: Color | str | None) -> Color | str | None:
        if color is None:
            setattr(self, self._internal_name, None)
        else:
            if isinstance(color, Color):
                setattr(self, self._internal_name, color)
            elif isinstance(color, str):
                new_color = Color.parse(color)
                setattr(self, self._internal_name, new_color)
        return color


class StyleFlagsProperty:

    _VALID_PROPERTIES = {
        "not",
        "bold",
        "italic",
        "underline",
        "overline",
        "strike",
        "b",
        "i",
        "u",
        "o",
    }

    def __set_name__(self, owner: Styles, name: str) -> None:
        self._name = name
        self._internal_name = f"_rule_{name}"

    def __get__(self, obj: Styles, objtype: type[Styles] | None = None) -> Style:
        return getattr(obj, self._internal_name, None) or Style.null()

    def __set__(self, obj: Styles, style_flags: str | None) -> str | None:
        if style_flags is None:
            setattr(self, self._internal_name, None)
        else:
            words = [word.strip() for word in style_flags.split(" ")]
            valid_word = self._VALID_PROPERTIES.__contains__
            for word in words:
                if not valid_word(word):
                    raise StyleValueError(f"unknown word {word!r} in style flags")
            style = Style.parse(" ".join(words))
            setattr(obj, self._internal_name, style)
        return style_flags
