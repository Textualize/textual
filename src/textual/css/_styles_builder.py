from __future__ import annotations

from typing import cast

import rich.repr
from rich.color import ANSI_COLOR_NAMES, Color
from rich.style import Style

from .constants import VALID_BORDER, VALID_DISPLAY, VALID_VISIBILITY
from .errors import DeclarationError, StyleValueError
from ._error_tools import friendly_list
from ..geometry import Offset, Spacing, SpacingDimensions
from .model import Declaration
from .styles import Styles
from .types import Display, Visibility
from .tokenize import Token


class StylesBuilder:
    def __init__(self) -> None:
        self.styles = Styles()

    def __rich_repr__(self) -> rich.repr.Result:
        yield "styles", self.styles

    def error(self, name: str, token: Token, message: str) -> None:
        raise DeclarationError(name, token, message)

    def add_declaration(self, declaration: Declaration) -> None:
        if not declaration.tokens:
            return
        process_method = getattr(
            self, f"process_{declaration.name.replace('-', '_')}", None
        )
        if process_method is None:
            self.error(
                declaration.name,
                declaration.token,
                f"unknown declaration {declaration.name!r}",
            )
        else:
            tokens = declaration.tokens
            if tokens[-1].name == "important":
                tokens = tokens[:-1]
                self.styles.important.add(declaration.name)
            if process_method is not None:
                try:
                    process_method(declaration.name, tokens)
                except DeclarationError as error:
                    self.error(error.name, error.token, error.message)
                except Exception as error:
                    self.error(declaration.name, declaration.token, str(error))

    def process_display(self, name: str, tokens: list[Token]) -> None:
        for token in tokens:
            _, _, location, name, value = token
            if name == "token":
                value = value.lower()
                if value in VALID_DISPLAY:
                    self.styles._rule_display = cast(Display, value)
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
            _, _, location, name, value = token
            if name == "token":
                value = value.lower()
                if value in VALID_VISIBILITY:
                    self.styles._rule_visibility = cast(Visibility, value)
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
            _, _, location, toke_name, value = token
            if toke_name == "number":
                append(int(value))
            else:
                self.error(name, token, f"unexpected token {value!r} in declaration")
        if len(space) not in (1, 2, 4):
            self.error(
                name, tokens[0], f"1, 2, or 4 values expected (received {len(space)})"
            )
        setattr(
            self.styles,
            f"_{name}",
            Spacing.unpack(cast(SpacingDimensions, tuple(space))),
        )

    def process_padding(self, name: str, tokens: list[Token]) -> None:
        self._process_space(name, tokens)

    def process_margin(self, name: str, tokens: list[Token]) -> None:
        self._process_space(name, tokens)

    def _parse_border(self, name: str, tokens: list[Token]) -> tuple[str, Style]:
        style = Style()
        border_type = "solid"
        style_tokens: list[str] = []
        append = style_tokens.append
        for token in tokens:
            _, _, location, token_name, value = token
            if token_name == "token":
                if value in VALID_BORDER:
                    border_type = value
                else:
                    append(value)
            elif token_name == "color":
                append(value)
            else:
                self.error(name, token, f"unexpected token {value!r} in declaration")
        style_definition = " ".join(style_tokens)
        try:
            style = Style.parse(style_definition)
        except Exception as error:
            self.error(name, tokens[0], f"error in {name} declaration; {error}")
        return (border_type, style)

    def _process_border(self, edge: str, name: str, tokens: list[Token]) -> None:
        border = self._parse_border("border", tokens)
        setattr(self.styles, f"_border_{edge}", border)

    def process_border(self, name: str, tokens: list[Token]) -> None:
        border = self._parse_border("border", tokens)
        styles = self.styles
        styles._rule_border_top = styles._rule_border_right = border
        styles._rule_border_bottom = styles._rule_border_left = border

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
        setattr(self.styles, f"_outline_{edge}", border)

    def process_outline(self, name: str, tokens: list[Token]) -> None:
        border = self._parse_border("outline", tokens)
        styles = self.styles
        styles._rule_outline_top = styles._rule_outline_right = border
        styles._rule_outline_bottom = styles._rule_outline_left = border

    def process_outline_top(self, name: str, tokens: list[Token]) -> None:
        self._process_outline("top", name, tokens)

    def process_parse_border_right(self, name: str, tokens: list[Token]) -> None:
        self._process_outline("right", name, tokens)

    def process_outline_bottom(self, name: str, tokens: list[Token]) -> None:
        self._process_outline("bottom", name, tokens)

    def process_outline_left(self, name: str, tokens: list[Token]) -> None:
        self._process_outline("left", name, tokens)

    def process_offset(self, name: str, tokens: list[Token]) -> None:
        if not tokens:
            return
        if len(tokens) != 2:
            self.error(name, tokens[0], "expected two numbers in declaration")
        else:
            token1, token2 = tokens
            if token1.name != "number":
                self.error(name, token1, f"expected a number (found {token1.value!r})")
            if token2.name != "number":
                self.error(name, token2, f"expected a number (found {token1.value!r})")
            self.styles._rule_offset = Offset(
                int(float(token1.value)), int(float(token2.value))
            )

    def process_offset_x(self, name: str, tokens: list[Token]) -> None:
        if not tokens:
            return
        if len(tokens) != 1:
            self.error(name, tokens[0], f"expected a single number")
        else:
            x = int(float(tokens[0].value))
            y = self.styles.offset.y
            self.styles._rule_offset = Offset(x, y)

    def process_offset_y(self, name: str, tokens: list[Token]) -> None:
        if not tokens:
            return
        if len(tokens) != 1:
            self.error(name, tokens[0], f"expected a single number")
        else:
            y = int(float(tokens[0].value))
            x = self.styles.offset.x
            self.styles._rule_offset = Offset(x, y)

    def process_layout(self, name: str, tokens: list[Token]) -> None:
        if tokens:
            if len(tokens) != 1:
                self.error(name, tokens[0], "unexpected tokens in declaration")
            else:
                self.styles._rule_layout = tokens[0].value

    def process_text(self, name: str, tokens: list[Token]) -> None:
        style_definition = " ".join(token.value for token in tokens)
        style = Style.parse(style_definition)
        self.styles.text = style

    def process_text_color(self, name: str, tokens: list[Token]) -> None:
        for token in tokens:
            if token.name in ("color", "token"):
                try:
                    self.styles._rule_text_color = Color.parse(token.value)
                except Exception as error:
                    self.error(
                        name, token, f"failed to parse color {token.value!r}; {error}"
                    )
            else:
                self.error(
                    name, token, f"unexpected token {token.value!r} in declaration"
                )

    def process_text_bgcolor(self, name: str, tokens: list[Token]) -> None:
        for token in tokens:
            if token.name in ("color", "token"):
                try:
                    self.styles._rule_text_bgcolor = Color.parse(token.value)
                except Exception as error:
                    self.error(
                        name, token, f"failed to parse color {token.value!r}; {error}"
                    )
            else:
                self.error(
                    name, token, f"unexpected token {token.value!r} in declaration"
                )

    def process_text_style(self, name: str, tokens: list[Token]) -> None:
        style_definition = " ".join(token.value for token in tokens)
        self.styles.text_style = style_definition

    def process_dock_group(self, name: str, tokens: list[Token]) -> None:

        if len(tokens) > 1:
            self.error(
                name,
                tokens[1],
                f"unexpected tokens in dock-group declaration",
            )
        self.styles._dock_group = tokens[0].value if tokens else ""

    def process_docks(self, name: str, tokens: list[Token]) -> None:
        docks: list[str] = []
        for token in tokens:
            if token.name == "token":
                docks.append(token.value)
            else:

                self.error(
                    name,
                    token,
                    f"unexpected token {token.value!r} in docks declaration",
                )
        self.styles._docks = tuple(docks)

    def process_dock_edge(self, name: str, tokens: list[Token]) -> None:
        if len(tokens) > 1:
            self.error(name, tokens[1], f"unexpected tokens in dock-edge declaration")
        try:
            self.styles.dock_edge = tokens[0].value if tokens else ""
        except StyleValueError as error:
            self.error(name, tokens[0], str(error))
