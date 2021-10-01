from __future__ import annotations

from dataclasses import dataclass, field
from typing import cast, TYPE_CHECKING

from rich import print
from rich.color import ANSI_COLOR_NAMES, Color

from ._error_tools import friendly_list
from .tokenize import Token
from .types import Visibility

if TYPE_CHECKING:
    from .model import Declaration


class DeclarationError(Exception):
    def __init__(self, name: str, token: Token, message: str) -> None:
        self.token = token
        super().__init__(message)


VALID_VISIBILITY = {"visible", "hidden"}
VALID_BORDER = {"rounded", "solid", "double", "dashed", "heavy", "inner", "outer"}


@dataclass
class Styles:

    visibility: Visibility | None = None

    border_top: tuple[str, Color] | None = None
    border_right: tuple[str, Color] | None = None
    border_bottom: tuple[str, Color] | None = None
    border_left: tuple[str, Color] | None = None

    outline_top: tuple[str, Color] | None = None
    outline_right: tuple[str, Color] | None = None
    outline_bottom: tuple[str, Color] | None = None
    outline_left: tuple[str, Color] | None = None

    important: set[str] = field(default_factory=set)

    def error(self, name: str, token: Token, msg: str) -> None:
        raise DeclarationError(name, token, msg)

    def add_declaration(self, declaration: Declaration) -> None:

        print(declaration)
        if not declaration.tokens:
            return
        process_method = getattr(self, f"process_{declaration.name.replace('-', '_')}")
        tokens = declaration.tokens
        if tokens[-1].name == "important":
            tokens = tokens[:-1]
            self.important.add(declaration.name)
        if process_method is not None:
            process_method(declaration.name, tokens)

    def _parse_border(self, tokens: list[Token]) -> tuple[str, Color]:
        color = Color.default()
        border_type = "solid"
        for token in tokens:
            location, name, value = token
            if name == "token":
                if value in ANSI_COLOR_NAMES:
                    color = Color.parse(value)
                elif value in VALID_BORDER:
                    border_type = value
                else:
                    self.error(name, token, f"unknown token {value!r} in declaration")
            elif name == "color":
                color = Color.parse(value)
            else:
                self.error(name, token, f"unexpected token {value!r} in declaration")
        return (border_type, color)

    def _process_border(self, edge: str, name: str, tokens: list[Token]) -> None:
        border = self._parse_border(tokens)
        setattr(self, f"border_{edge}", border)

    def process_border(self, name: str, tokens: list[Token]) -> None:
        border = self._parse_border(tokens)
        self.border_top = self.border_right = border
        self.border_bottom = self.border_left = border

    def process_border_top(self, name: str, tokens: list[Token]) -> None:
        self._process_border("top", name, tokens)

    def process_border_right(self, name: str, tokens: list[Token]) -> None:
        self._process_border("right", name, tokens)

    def process_border_bottom(self, name: str, tokens: list[Token]) -> None:
        self._process_border("bottom", name, tokens)

    def process_border_left(self, name: str, tokens: list[Token]) -> None:
        self._process_border("left", name, tokens)

    def _process_outline(self, edge: str, name: str, tokens: list[Token]) -> None:
        border = self._parse_border(tokens)
        setattr(self, f"outline_{edge}", border)

    def process_outline(self, name: str, tokens: list[Token]) -> None:
        border = self._parse_border(tokens)
        self.outline_top = self.outline_right = border
        self.outline_bottom = self.outline_left = border

    def process_outline_top(self, name: str, tokens: list[Token]) -> None:
        self._process_outline("top", name, tokens)

    def process_parse_border_right(self, name: str, tokens: list[Token]) -> None:
        self._process_outline("right", name, tokens)

    def process_outline_bottom(self, name: str, tokens: list[Token]) -> None:
        self._process_outline("bottom", name, tokens)

    def process_outline_left(self, name: str, tokens: list[Token]) -> None:
        self._process_outline("left", name, tokens)

    def process_visibility(self, name: str, tokens: list[Token]) -> None:
        for token in tokens:
            location, name, value = token
            if name == "token":
                value = value.lower()
                if value in VALID_VISIBILITY:
                    self.visibility = cast(Visibility, value)
                else:
                    self.error(
                        name,
                        token,
                        f"invalid value for visibility (received {value!r}, expected {friendly_list(VALID_VISIBILITY)})",
                    )
            else:
                self.error(name, token, f"invalid token {value!r} in this context")
