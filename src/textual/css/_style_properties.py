from __future__ import annotations

from typing import Iterable, NamedTuple, Sequence, TYPE_CHECKING

import rich.repr
from rich.color import Color
from rich.style import Style


from ..geometry import Offset, Spacing, SpacingDimensions
from .constants import NULL_SPACING
from .errors import StyleValueError

if TYPE_CHECKING:
    from .styles import Styles


class _BoxProperty:

    DEFAULT = ("", Style())

    def __set_name__(self, owner: Styles, name: str) -> None:
        self.internal_name = f"_{name}"
        _type, edge = name.split("_")
        self._type = _type
        self.edge = edge

    def __get__(self, obj: Styles, objtype=None) -> tuple[str, Style]:
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
    top: tuple[str, Style]
    right: tuple[str, Style]
    bottom: tuple[str, Style]
    left: tuple[str, Style]

    def __rich_repr__(self) -> rich.repr.Result:
        if self.top[0]:
            yield "top", self.top
        if self.right[0]:
            yield "right", self.right
        if self.bottom[0]:
            yield "bottom", self.bottom
        if self.left[0]:
            yield "left", self.left


class _BorderProperty:
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


class _StyleProperty:
    def __set_name__(self, owner: Styles, name: str) -> None:
        self._internal_name = f"_{name}"

    def __get__(self, obj: Styles, objtype: type[Styles] | None = None) -> Style:
        return getattr(obj, self._internal_name)

    def __set__(self, obj: Styles, style: Style | str) -> Style:
        if isinstance(style, str):
            _style = Style.parse(style)
        else:
            _style = style
        setattr(obj, self._internal_name, _style)
        return _style


class _SpacingProperty:
    def __set_name__(self, owner: Styles, name: str) -> None:
        self._internal_name = f"_{name}"

    def __get__(self, obj: Styles, objtype: type[Styles] | None = None) -> Spacing:
        return getattr(obj, self._internal_name) or NULL_SPACING

    def __set__(self, obj: Styles, spacing: SpacingDimensions) -> Spacing:
        spacing = Spacing.unpack(spacing)
        setattr(obj, self._internal_name, spacing)
        return spacing


class _DocksProperty:
    def __get__(
        self, obj: Styles, objtype: type[Styles] | None = None
    ) -> tuple[str, ...]:
        return obj._docks or ()

    def __set__(self, obj: Styles, docks: str | Iterable[str]) -> tuple[str, ...]:
        if isinstance(docks, str):
            _docks = tuple(name.lower().strip() for name in docks.split(" "))
        else:
            _docks = tuple(docks)
        obj._docks = _docks
        return _docks


class _DockGroupProperty:
    def __get__(self, obj: Styles, objtype: type[Styles] | None = None) -> str:
        return obj._dock_group or ""

    def __set__(self, obj: Styles, spacing: str | None) -> str | None:
        obj._dock_group = spacing
        return spacing


class _OffsetProperty:
    def __set_name__(self, owner: Styles, name: str) -> None:
        self._internal_name = f"_{name}"

    def __get__(self, obj: Styles, objtype: type[Styles] | None = None) -> Offset:
        return getattr(obj, self._internal_name) or Offset()

    def __set__(self, obj: Styles, offset: tuple[int, int]) -> tuple[int, int]:
        _offset = Offset(*offset)
        setattr(obj, self._internal_name, _offset)
        return offset
