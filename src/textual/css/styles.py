from __future__ import annotations

from dataclasses import dataclass, field
from typing import cast, Sequence, TYPE_CHECKING

from rich import print
import rich.repr
from rich.color import ANSI_COLOR_NAMES, Color

from ._error_tools import friendly_list
from ..geometry import Spacing, SpacingDimensions
from .tokenize import Token
from .types import Display, Visibility

if TYPE_CHECKING:
    from .model import Declaration


class DeclarationError(Exception):
    def __init__(self, name: str, token: Token, message: str) -> None:
        self.token = token
        super().__init__(message)


VALID_VISIBILITY = {"visible", "hidden"}
VALID_DISPLAY = {"block", "none"}
VALID_BORDER = {"rounded", "solid", "double", "dashed", "heavy", "inner", "outer"}


NULL_SPACING = Spacing(0, 0, 0, 0)


class _BoxSetter:
    def __set_name__(self, owner, name):
        self.internal_name = f"_{name}"
        _type, edge = name.split("_")
        self._type = _type
        self.edge = edge

    def __get__(self, obj: Styles, objtype=None) -> tuple[str, str] | None:
        value = getattr(obj, self.internal_name)
        if value is None:
            return None
        else:
            _type, color = value
            return (_type, color.name)

    def __set__(
        self, obj: Styles, border: tuple[str, str] | None
    ) -> tuple[str, Color] | None:
        if border is None:
            new_value = None
        else:
            _type, color = border
            if isinstance(color, Color):
                new_value = (_type, color)
            else:
                new_value = (_type, Color.parse(color))
        setattr(obj, self.internal_name, new_value)
        return new_value


@dataclass
class Styles:

    _display: Display | None = None
    _visibility: Visibility | None = None

    _padding: Spacing | None = None
    _margin: Spacing | None = None

    _border_top: tuple[str, Color] | None = None
    _border_right: tuple[str, Color] | None = None
    _border_bottom: tuple[str, Color] | None = None
    _border_left: tuple[str, Color] | None = None

    _outline_top: tuple[str, Color] | None = None
    _outline_right: tuple[str, Color] | None = None
    _outline_bottom: tuple[str, Color] | None = None
    _outline_left: tuple[str, Color] | None = None

    _important: set[str] = field(default_factory=set)

    @property
    def display(self) -> Display:
        return self._display or "block"

    @display.setter
    def display(self, display: Display) -> None:
        if display not in VALID_DISPLAY:
            raise ValueError(f"display must be one of {friendly_list(VALID_DISPLAY)}")
        self._display = display

    @property
    def visibility(self) -> Visibility:
        return self._visibility or "visible"

    @visibility.setter
    def visibility(self, visibility: Visibility) -> None:
        if visibility not in VALID_VISIBILITY:
            raise ValueError(
                f"visibility must be one of {friendly_list(VALID_VISIBILITY)}"
            )
        self._visibility = visibility

    @property
    def padding(self) -> Spacing:
        return self._padding or NULL_SPACING

    @padding.setter
    def padding(self, padding: SpacingDimensions) -> None:
        self._padding = Spacing.unpack(padding)

    @property
    def margin(self) -> Spacing:
        return self._margin or NULL_SPACING

    @margin.setter
    def margin(self, padding: SpacingDimensions) -> None:
        self._margin = Spacing.unpack(padding)

    @property
    def border(
        self,
    ) -> tuple[
        tuple[str, str] | None,
        tuple[str, str] | None,
        tuple[str, str] | None,
        tuple[str, str] | None,
    ]:
        return (
            self.border_top,
            self.border_right,
            self.border_bottom,
            self.border_left,
        )

    @border.setter
    def border(
        self, border: Sequence[tuple[str, str] | None] | tuple[str, str] | None
    ) -> None:
        if border is None:
            self._border_top = (
                self._border_right
            ) = self._border_bottom = self._border_left = None
            return
        if isinstance(border, tuple):
            self.border_top = (
                self.border_right
            ) = self.border_bottom = self.border_left = border
            return
        count = len(border)
        if count == 1:
            self.border_top = (
                self.border_right
            ) = self.border_bottom = self.border_left = border[0]
        elif count == 2:
            self.border_top = self.border_right = border[0]
            self.border_bottom = self.border_left = border[1]
        elif count == 4:
            top, right, bottom, left = border
            self.border_top = top
            self.border_right = right
            self.border_bottom = bottom
            self.border_left = left
        else:
            raise ValueError("expected 1, 2, or 4 values")

    border_top = _BoxSetter()
    border_right = _BoxSetter()
    border_bottom = _BoxSetter()
    border_left = _BoxSetter()

    outline_top = _BoxSetter()
    outline_right = _BoxSetter()
    outline_bottom = _BoxSetter()
    outline_left = _BoxSetter()

    def __rich_repr__(self) -> rich.repr.Result:
        yield "display", self.display, "block"
        yield "visibility", self.visibility, "visible"
        yield "padding", self.padding, NULL_SPACING
        yield "margin", self.margin, NULL_SPACING

        yield "border_top", self.border_top, None
        yield "border_right", self.border_right, None
        yield "border_bottom", self.border_bottom, None
        yield "border_left", self.border_left, None

        yield "outline_top", self.outline_top, None
        yield "outline_right", self.outline_right, None
        yield "outline_bottom", self.outline_bottom, None
        yield "outline_left", self.outline_left, None

    @property
    def css_lines(self) -> list[str]:
        lines: list[str] = []
        append = lines.append

        def append_declaration(name: str, value: str) -> None:
            if name in self._important:
                append(f"{name}: {value} !important;")
            else:
                append(f"{name}: {value};")

        if self._display is not None:
            append_declaration("display", self._display)

        if self._visibility is not None:
            append_declaration("visibility", self._visibility)

        if self._padding is not None:
            append_declaration("padding", self._padding.packed)

        if self._margin is not None:
            append_declaration("margin", self._margin.packed)

        if (
            self._border_top != None
            and self._border_top == self._border_right
            and self._border_right == self._border_bottom
            and self._border_bottom == self._border_left
        ):
            _type, color = self._border_top
            append_declaration("border", f"{_type} {color.name}")
        else:

            if self._border_top is not None:
                _type, color = self._border_top
                append_declaration("border-top", f"{_type} {color.name}")

            if self._border_right is not None:
                _type, color = self._border_right
                append_declaration("border-right", f"{_type} {color.name}")

            if self._border_bottom is not None:
                _type, color = self._border_bottom
                append_declaration("border-bottom", f"{_type} {color.name}")

            if self._border_left is not None:
                _type, color = self._border_left
                append_declaration("border-left", f"{_type} {color.name}")

        if (
            self._outline_top != None
            and self._outline_top == self._outline_right
            and self._outline_right == self._outline_bottom
            and self._outline_bottom == self._outline_left
        ):
            _type, color = self._outline_top
            append_declaration("outline", f"{_type} {color.name}")
        else:

            if self._outline_top is not None:
                _type, color = self._outline_top
                append_declaration("outline-top", f"{_type} {color.name}")

            if self._outline_right is not None:
                _type, color = self._outline_right
                append_declaration("outline-right", f"{_type} {color.name}")

            if self._outline_bottom is not None:
                _type, color = self._outline_bottom
                append_declaration("outline-bottom", f"{_type} {color.name}")

            if self._outline_left is not None:
                _type, color = self._outline_left
                append_declaration("outline-left", f"{_type} {color.name}")

        return lines

    def error(self, name: str, token: Token, msg: str) -> None:
        line, col = token.location
        raise DeclarationError(name, token, f"{msg} (line {line + 1}, col {col + 1})")

    def add_declaration(self, declaration: Declaration) -> None:
        if not declaration.tokens:
            return
        process_method = getattr(self, f"process_{declaration.name.replace('-', '_')}")
        tokens = declaration.tokens
        if tokens[-1].name == "important":
            tokens = tokens[:-1]
            self._important.add(declaration.name)
        if process_method is not None:
            process_method(declaration.name, tokens)

    def process_display(self, name: str, tokens: list[Token]) -> None:
        for token in tokens:
            location, name, value = token
            if name == "token":
                value = value.lower()
                if value in VALID_DISPLAY:
                    self._display = cast(Display, value)
                else:
                    self.error(
                        name,
                        token,
                        f"invalid value for display (received {value!r}, expected {friendly_list(VALID_DISPLAY)})",
                    )
            else:
                self.error(name, token, f"invalid token {value!r} in this context")

    def process_visibility(self, name: str, tokens: list[Token]) -> None:
        for token in tokens:
            location, name, value = token
            if name == "token":
                value = value.lower()
                if value in VALID_VISIBILITY:
                    self._visibility = cast(Visibility, value)
                else:
                    self.error(
                        name,
                        token,
                        f"invalid value for visibility (received {value!r}, expected {friendly_list(VALID_VISIBILITY)})",
                    )
            else:
                self.error(name, token, f"invalid token {value!r} in this context")

    def _process_space(self, name: str, tokens: list[Token]) -> None:
        space: list[int] = []
        append = space.append
        for token in tokens:
            location, toke_name, value = token
            if toke_name == "number":
                append(int(value))
            else:
                self.error(name, token, f"unexpected token {value!r} in declaration")
        if len(space) not in (1, 2, 4):
            self.error(
                name, tokens[0], f"1, 2, or 4 values expected (received {len(space)})"
            )
        setattr(self, f"_{name}", Spacing.unpack(cast(SpacingDimensions, tuple(space))))

    def process_padding(self, name: str, tokens: list[Token]) -> None:
        self._process_space(name, tokens)

    def process_margin(self, name: str, tokens: list[Token]) -> None:
        self._process_space(name, tokens)

    def _parse_border(self, name: str, tokens: list[Token]) -> tuple[str, Color]:
        color = Color.default()
        border_type = "solid"
        for token in tokens:
            location, token_name, value = token
            if token_name == "token":
                if value in ANSI_COLOR_NAMES:
                    color = Color.parse(value)
                elif value in VALID_BORDER:
                    border_type = value
                else:
                    self.error(name, token, f"unknown token {value!r} in declaration")
            elif token_name == "color":
                color = Color.parse(value)
            else:
                self.error(name, token, f"unexpected token {value!r} in declaration")
        return (border_type, color)

    def _process_border(self, edge: str, name: str, tokens: list[Token]) -> None:
        border = self._parse_border("border", tokens)
        setattr(self, f"_border_{edge}", border)

    def process_border(self, name: str, tokens: list[Token]) -> None:
        border = self._parse_border("border", tokens)
        self._border_top = self._border_right = border
        self._border_bottom = self._border_left = border

    def process_border_top(self, name: str, tokens: list[Token]) -> None:
        self._process_border("top", name, tokens)

    def process_border_right(self, name: str, tokens: list[Token]) -> None:
        self._process_border("right", name, tokens)

    def process_border_bottom(self, name: str, tokens: list[Token]) -> None:
        self._process_border("bottom", name, tokens)

    def process_border_left(self, name: str, tokens: list[Token]) -> None:
        self._process_border("left", name, tokens)

    def _process_outline(self, edge: str, name: str, tokens: list[Token]) -> None:
        border = self._parse_border("outline", tokens)
        setattr(self, f"_outline_{edge}", border)

    def process_outline(self, name: str, tokens: list[Token]) -> None:
        border = self._parse_border("outline", tokens)
        self._outline_top = self._outline_right = border
        self._outline_bottom = self._outline_left = border

    def process_outline_top(self, name: str, tokens: list[Token]) -> None:
        self._process_outline("top", name, tokens)

    def process_parse_border_right(self, name: str, tokens: list[Token]) -> None:
        self._process_outline("right", name, tokens)

    def process_outline_bottom(self, name: str, tokens: list[Token]) -> None:
        self._process_outline("bottom", name, tokens)

    def process_outline_left(self, name: str, tokens: list[Token]) -> None:
        self._process_outline("left", name, tokens)


if __name__ == "__main__":
    styles = Styles()

    styles.display = "none"
    styles.visibility = "hidden"
    styles.border = ("solid", "rgb(10,20,30)")
    styles.outline_right = ("solid", "red")

    from rich import print

    print(styles)
