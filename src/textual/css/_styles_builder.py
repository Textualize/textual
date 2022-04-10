from __future__ import annotations

from typing import cast, Iterable, NoReturn

import rich.repr
from rich.style import Style

from ._error_tools import friendly_list
from .constants import (
    VALID_BORDER,
    VALID_BOX_SIZING,
    VALID_EDGE,
    VALID_DISPLAY,
    VALID_OVERFLOW,
    VALID_VISIBILITY,
)
from .errors import DeclarationError
from .model import Declaration
from .scalar import Scalar, ScalarOffset, Unit, ScalarError
from .styles import DockGroup, Styles
from .tokenize import Token
from .transition import Transition
from .types import BoxSizing, Edge, Display, Overflow, Visibility
from ..color import Color
from .._duration import _duration_as_seconds
from .._easing import EASING
from ..geometry import Spacing, SpacingDimensions, clamp


def _join_tokens(tokens: Iterable[Token], joiner: str = "") -> str:
    """Convert tokens into a string by joining their values

    Args:
        tokens (Iterable[Token]): Tokens to join
        joiner (str): String to join on, defaults to ""

    Returns:
        str: The tokens, joined together to form a string.
    """
    return joiner.join(token.value for token in tokens)


class StylesBuilder:
    """
    The StylesBuilder object takes tokens parsed from the CSS and converts
    to the appropriate internal types.
    """

    def __init__(self) -> None:
        self.styles = Styles()

    def __rich_repr__(self) -> rich.repr.Result:
        yield "styles", self.styles

    def __repr__(self) -> str:
        return "StylesBuilder()"

    def error(self, name: str, token: Token, message: str) -> NoReturn:
        raise DeclarationError(name, token, message)

    def add_declaration(self, declaration: Declaration) -> None:
        if not declaration.tokens:
            return
        rule_name = declaration.name.replace("-", "_")
        process_method = getattr(self, f"process_{rule_name}", None)

        if process_method is None:
            self.error(
                declaration.name,
                declaration.token,
                f"unknown declaration {declaration.name!r}",
            )
        else:
            tokens = declaration.tokens

            important = tokens[-1].name == "important"
            if important:
                tokens = tokens[:-1]
                self.styles.important.add(rule_name)
            try:
                process_method(declaration.name, tokens, important)
            except DeclarationError:
                raise
            except Exception as error:
                self.error(declaration.name, declaration.token, str(error))

    def _process_enum_multiple(
        self, name: str, tokens: list[Token], valid_values: set[str], count: int
    ) -> tuple[str, ...]:
        """Generic code to process a declaration with two enumerations, like overflow: auto auto"""
        if len(tokens) > count or not tokens:
            self.error(name, tokens[0], f"expected 1 to {count} tokens here")
        results = []
        append = results.append
        for token in tokens:
            token_name, value, _, _, location, _ = token
            if token_name != "token":
                self.error(
                    name,
                    token,
                    f"invalid token {value!r}; expected {friendly_list(valid_values)}",
                )
            append(value)

        short_results = results[:]

        while len(results) < count:
            results.extend(short_results)
        results = results[:count]

        return tuple(results)

    def _process_enum(
        self, name: str, tokens: list[Token], valid_values: set[str]
    ) -> str:
        """Process a declaration that expects an enum.

        Args:
            name (str): Name of declaration.
            tokens (list[Token]): Tokens from parser.
            valid_values (list[str]): A set of valid values.

        Returns:
            bool: True if the value is valid or False if it is invalid (also generates an error)
        """

        if len(tokens) != 1:
            self.error(name, tokens[0], "expected a single token here")
            return False

        token = tokens[0]
        token_name, value, _, _, location, _ = token
        if token_name != "token":
            self.error(
                name,
                token,
                f"invalid token {value!r}, expected {friendly_list(valid_values)}",
            )
        if value not in valid_values:
            self.error(
                name,
                token,
                f"invalid value {value!r} for {name}, expected {friendly_list(valid_values)}",
            )
        return value

    def process_display(self, name: str, tokens: list[Token], important: bool) -> None:
        for token in tokens:
            name, value, _, _, location, _ = token

            if name == "token":
                value = value.lower()
                if value in VALID_DISPLAY:
                    self.styles._rules["display"] = cast(Display, value)
                else:
                    self.error(
                        name,
                        token,
                        f"invalid value for display (received {value!r}, expected {friendly_list(VALID_DISPLAY)})",
                    )
            else:
                self.error(name, token, f"invalid token {value!r} in this context")

    def _process_scalar(self, name: str, tokens: list[Token]) -> None:
        if not tokens:
            return
        if len(tokens) == 1:
            self.styles._rules[name.replace("-", "_")] = Scalar.parse(tokens[0].value)
        else:
            self.error(name, tokens[0], "a single scalar is expected")

    def process_box_sizing(
        self, name: str, tokens: list[Token], important: bool
    ) -> None:
        for token in tokens:
            name, value, _, _, location, _ = token

            if name == "token":
                value = value.lower()
                if value in VALID_BOX_SIZING:
                    self.styles._rules["box_sizing"] = cast(BoxSizing, value)
                else:
                    self.error(
                        name,
                        token,
                        f"invalid value for box-sizing (received {value!r}, expected {friendly_list(VALID_BOX_SIZING)})",
                    )
            else:
                self.error(name, token, f"invalid token {value!r} in this context")

    def process_width(self, name: str, tokens: list[Token], important: bool) -> None:
        self._process_scalar(name, tokens)

    def process_height(self, name: str, tokens: list[Token], important: bool) -> None:
        self._process_scalar(name, tokens)

    def process_min_width(
        self, name: str, tokens: list[Token], important: bool
    ) -> None:
        self._process_scalar(name, tokens)

    def process_min_height(
        self, name: str, tokens: list[Token], important: bool
    ) -> None:
        self._process_scalar(name, tokens)

    def process_max_width(
        self, name: str, tokens: list[Token], important: bool
    ) -> None:
        self._process_scalar(name, tokens)

    def process_max_height(
        self, name: str, tokens: list[Token], important: bool
    ) -> None:
        self._process_scalar(name, tokens)

    def process_overflow(self, name: str, tokens: list[Token], important: bool) -> None:
        rules = self.styles._rules
        overflow_x, overflow_y = self._process_enum_multiple(
            name, tokens, VALID_OVERFLOW, 2
        )
        rules["overflow_x"] = cast(Overflow, overflow_x)
        rules["overflow_y"] = cast(Overflow, overflow_y)

    def process_overflow_x(
        self, name: str, tokens: list[Token], important: bool
    ) -> None:
        self.styles._rules["overflow_x"] = cast(
            Overflow, self._process_enum(name, tokens, VALID_OVERFLOW)
        )

    def process_overflow_y(
        self, name: str, tokens: list[Token], important: bool
    ) -> None:
        self.styles._rules["overflow_y"] = cast(
            Overflow, self._process_enum(name, tokens, VALID_OVERFLOW)
        )

    def process_visibility(
        self, name: str, tokens: list[Token], important: bool
    ) -> None:
        for token in tokens:
            name, value, _, _, location, _ = token
            if name == "token":
                value = value.lower()
                if value in VALID_VISIBILITY:
                    self.styles._rules["visibility"] = cast(Visibility, value)
                else:
                    self.error(
                        name,
                        token,
                        f"property 'visibility' has invalid value {value!r}; expected {friendly_list(VALID_VISIBILITY)}",
                    )
            else:
                self.error(name, token, f"invalid token {value!r} in this context")

    def process_opacity(self, name: str, tokens: list[Token], important: bool) -> None:
        if not tokens:
            return
        token = tokens[0]
        error = False
        if len(tokens) != 1:
            error = True
        else:
            token_name = token.name
            value = token.value
            if token_name == "scalar" and value.endswith("%"):
                percentage = value[:-1]
                try:
                    opacity = clamp(float(percentage) / 100, 0, 1)
                    self.styles.set_rule(name, opacity)
                except ValueError:
                    error = True
            elif token_name == "number":
                try:
                    opacity = clamp(float(value), 0, 1)
                    self.styles.set_rule(name, opacity)
                except ValueError:
                    error = True
            else:
                error = True

        if error:
            self.error(
                name,
                token,
                f"property 'opacity' has invalid value {_join_tokens(tokens)!r}; "
                f"expected a percentage or float between 0 and 1; "
                f"example valid values: '0.4', '40%'",
            )

    def _process_space(self, name: str, tokens: list[Token]) -> None:
        space: list[int] = []
        append = space.append
        for token in tokens:
            token_name, value, _, _, location, _ = token
            if token_name in ("number", "scalar"):
                try:
                    append(int(value))
                except ValueError:
                    self.error(name, token, f"expected a number here; found {value!r}")
            else:
                self.error(name, token, f"unexpected token {value!r} in declaration")
        if len(space) not in (1, 2, 4):
            self.error(
                name, tokens[0], f"1, 2, or 4 values expected; received {len(space)}"
            )
        self.styles._rules[name] = Spacing.unpack(cast(SpacingDimensions, tuple(space)))

    def process_padding(self, name: str, tokens: list[Token], important: bool) -> None:
        self._process_space(name, tokens)

    def process_margin(self, name: str, tokens: list[Token], important: bool) -> None:
        self._process_space(name, tokens)

    def _parse_border(self, name: str, tokens: list[Token]) -> tuple[str, Color]:
        border_type = "solid"
        border_color = Color(0, 255, 0)

        for token in tokens:
            token_name, value, _, _, _, _ = token
            if token_name == "token":
                if value in VALID_BORDER:
                    border_type = value
                else:
                    border_color = Color.parse(value)

            elif token_name == "color":
                border_color = Color.parse(value)
            else:
                self.error(name, token, f"unexpected token {value!r} in declaration")

        return (border_type, border_color)

    def _process_border_edge(self, edge: str, name: str, tokens: list[Token]) -> None:
        border = self._parse_border("border", tokens)
        self.styles._rules[f"border_{edge}"] = border

    def process_border(self, name: str, tokens: list[Token], important: bool) -> None:
        border = self._parse_border("border", tokens)
        rules = self.styles._rules
        rules["border_top"] = rules["border_right"] = border
        rules["border_bottom"] = rules["border_left"] = border

    def process_border_top(
        self, name: str, tokens: list[Token], important: bool
    ) -> None:
        self._process_border_edge("top", name, tokens)

    def process_border_right(
        self, name: str, tokens: list[Token], important: bool
    ) -> None:
        self._process_border_edge("right", name, tokens)

    def process_border_bottom(
        self, name: str, tokens: list[Token], important: bool
    ) -> None:
        self._process_border_edge("bottom", name, tokens)

    def process_border_left(
        self, name: str, tokens: list[Token], important: bool
    ) -> None:
        self._process_border_edge("left", name, tokens)

    def _process_outline(self, edge: str, name: str, tokens: list[Token]) -> None:
        border = self._parse_border("outline", tokens)
        self.styles._rules[f"outline_{edge}"] = border

    def process_outline(self, name: str, tokens: list[Token], important: bool) -> None:
        border = self._parse_border("outline", tokens)
        rules = self.styles._rules
        rules["outline_top"] = rules["outline_right"] = border
        rules["outline_bottom"] = rules["outline_left"] = border

    def process_outline_top(
        self, name: str, tokens: list[Token], important: bool
    ) -> None:
        self._process_outline("top", name, tokens)

    def process_parse_border_right(
        self, name: str, tokens: list[Token], important: bool
    ) -> None:
        self._process_outline("right", name, tokens)

    def process_outline_bottom(
        self, name: str, tokens: list[Token], important: bool
    ) -> None:
        self._process_outline("bottom", name, tokens)

    def process_outline_left(
        self, name: str, tokens: list[Token], important: bool
    ) -> None:
        self._process_outline("left", name, tokens)

    def process_offset(self, name: str, tokens: list[Token], important: bool) -> None:
        if not tokens:
            return
        if len(tokens) != 2:
            self.error(
                name, tokens[0], "expected two scalars or numbers in declaration"
            )
        else:
            token1, token2 = tokens

            if token1.name not in ("scalar", "number"):
                self.error(
                    name, token1, f"expected a scalar or number; found {token1.value!r}"
                )
            if token2.name not in ("scalar", "number"):
                self.error(
                    name, token2, f"expected a scalar or number; found {token2.value!r}"
                )

            scalar_x = Scalar.parse(token1.value, Unit.WIDTH)
            scalar_y = Scalar.parse(token2.value, Unit.HEIGHT)
            self.styles._rules["offset"] = ScalarOffset(scalar_x, scalar_y)

    def process_offset_x(self, name: str, tokens: list[Token], important: bool) -> None:
        if not tokens:
            return
        if len(tokens) != 1:
            self.error(name, tokens[0], f"expected a single number")
        else:
            token = tokens[0]
            if token.name not in ("scalar", "number"):
                self.error(name, token, f"expected a scalar; found {token.value!r}")
            x = Scalar.parse(token.value, Unit.WIDTH)
            y = self.styles.offset.y
            self.styles._rules["offset"] = ScalarOffset(x, y)

    def process_offset_y(self, name: str, tokens: list[Token], important: bool) -> None:
        if not tokens:
            return
        if len(tokens) != 1:
            self.error(name, tokens[0], f"expected a single number")
        else:
            token = tokens[0]
            if token.name not in ("scalar", "number"):
                self.error(name, token, f"expected a scalar; found {token.value!r}")
            y = Scalar.parse(token.value, Unit.HEIGHT)
            x = self.styles.offset.x
            self.styles._rules["offset"] = ScalarOffset(x, y)

    def process_layout(self, name: str, tokens: list[Token], important: bool) -> None:
        from ..layouts.factory import get_layout, MissingLayout, LAYOUT_MAP

        if tokens:
            if len(tokens) != 1:
                self.error(name, tokens[0], "unexpected tokens in declaration")
            else:
                value = tokens[0].value
                layout_name = value
                try:
                    self.styles._rules["layout"] = get_layout(layout_name)
                except MissingLayout:
                    self.error(
                        name,
                        tokens[0],
                        f"invalid value for layout (received {value!r}, expected {friendly_list(LAYOUT_MAP.keys())})",
                    )

    def process_color(self, name: str, tokens: list[Token], important: bool) -> None:
        name = name.replace("-", "_")
        for token in tokens:
            if token.name in ("color", "token"):
                try:
                    self.styles._rules[name] = Color.parse(token.value)
                except Exception as error:
                    self.error(
                        name, token, f"failed to parse color {token.value!r}; {error}"
                    )
            else:
                self.error(
                    name, token, f"unexpected token {token.value!r} in declaration"
                )

    def process_background(
        self, name: str, tokens: list[Token], important: bool
    ) -> None:
        self.process_color(name, tokens, important)

    def process_scrollbar_color(
        self, name: str, tokens: list[Token], important: bool
    ) -> None:
        self.process_color(name, tokens, important)

    def process_scrollbar_color_hover(
        self, name: str, tokens: list[Token], important: bool
    ) -> None:
        self.process_color(name, tokens, important)

    def process_scrollbar_color_active(
        self, name: str, tokens: list[Token], important: bool
    ) -> None:
        self.process_color(name, tokens, important)

    def process_scrollbar_background(
        self, name: str, tokens: list[Token], important: bool
    ) -> None:
        self.process_color(name, tokens, important)

    def process_scrollbar_background_hover(
        self, name: str, tokens: list[Token], important: bool
    ) -> None:
        self.process_color(name, tokens, important)

    def process_scrollbar_background_active(
        self, name: str, tokens: list[Token], important: bool
    ) -> None:
        self.process_color(name, tokens, important)

    def process_text_style(
        self, name: str, tokens: list[Token], important: bool
    ) -> None:
        style_definition = " ".join(token.value for token in tokens)
        self.styles.text_style = style_definition

    def process_dock(self, name: str, tokens: list[Token], important: bool) -> None:

        if len(tokens) > 1:
            self.error(
                name,
                tokens[1],
                f"unexpected tokens in dock declaration",
            )
        self.styles._rules["dock"] = tokens[0].value if tokens else ""

    def process_docks(self, name: str, tokens: list[Token], important: bool) -> None:
        docks: list[DockGroup] = []
        for token in tokens:
            if token.name == "key_value":
                key, edge_name = token.value.split("=")
                edge_name = edge_name.strip().lower()
                edge_name, _, number = edge_name.partition("/")
                z = 0
                if number:
                    if not number.isdigit():
                        self.error(
                            name, token, f"expected integer after /, found {number!r}"
                        )
                    z = int(number)
                if edge_name not in VALID_EDGE:
                    self.error(
                        name,
                        token,
                        f"edge must be one of 'top', 'right', 'bottom', or 'left'; found {edge_name!r}",
                    )
                docks.append(DockGroup(key.strip(), cast(Edge, edge_name), z))
            elif token.name == "bar":
                pass
            else:
                self.error(
                    name,
                    token,
                    f"unexpected token {token.value!r} in docks declaration",
                )
        self.styles._rules["docks"] = tuple(docks + [DockGroup("_default", "top", 0)])

    def process_layer(self, name: str, tokens: list[Token], important: bool) -> None:
        if len(tokens) > 1:
            self.error(name, tokens[1], f"unexpected tokens in dock-edge declaration")
        self.styles._rules["layer"] = tokens[0].value

    def process_layers(self, name: str, tokens: list[Token], important: bool) -> None:
        layers: list[str] = []
        for token in tokens:
            if token.name != "token":
                self.error(name, token, "{token.name} not expected here")
            layers.append(token.value)
        self.styles._rules["layers"] = tuple(layers)

    def process_transition(
        self, name: str, tokens: list[Token], important: bool
    ) -> None:
        transitions: dict[str, Transition] = {}

        def make_groups() -> Iterable[list[Token]]:
            """Batch tokens into comma-separated groups."""
            group: list[Token] = []
            for token in tokens:
                if token.name == "comma":
                    if group:
                        yield group
                    group = []
                else:
                    group.append(token)
            if group:
                yield group

        valid_duration_token_names = ("duration", "number")
        for tokens in make_groups():
            css_property = ""
            duration = 1.0
            easing = "linear"
            delay = 0.0

            try:
                iter_tokens = iter(tokens)
                token = next(iter_tokens)
                if token.name != "token":
                    self.error(name, token, "expected property")

                css_property = token.value
                token = next(iter_tokens)
                if token.name not in valid_duration_token_names:
                    self.error(name, token, "expected duration or number")
                try:
                    duration = _duration_as_seconds(token.value)
                except ScalarError as error:
                    self.error(name, token, str(error))

                token = next(iter_tokens)
                if token.name != "token":
                    self.error(name, token, "easing function expected")

                if token.value not in EASING:
                    self.error(
                        name,
                        token,
                        f"expected easing function; found {token.value!r}",
                    )
                easing = token.value

                token = next(iter_tokens)
                if token.name not in valid_duration_token_names:
                    self.error(name, token, "expected duration or number")
                try:
                    delay = _duration_as_seconds(token.value)
                except ScalarError as error:
                    self.error(name, token, str(error))
            except StopIteration:
                pass
            transitions[css_property] = Transition(duration, easing, delay)

        self.styles._rules["transitions"] = transitions
