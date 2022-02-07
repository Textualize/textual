from __future__ import annotations

from typing import cast, Iterable, NoReturn

import rich.repr
from rich.color import Color
from rich.style import Style

from ._error_tools import friendly_list
from .constants import VALID_BORDER, VALID_EDGE, VALID_DISPLAY, VALID_VISIBILITY
from .errors import DeclarationError
from .model import Declaration
from .scalar import Scalar, ScalarOffset, Unit, ScalarError
from .styles import DockGroup, Styles
from .tokenize import Token
from .transition import Transition
from .types import Edge, Display, Visibility
from .._duration import _duration_as_seconds
from .._easing import EASING
from .._loop import loop_last
from ..geometry import Spacing, SpacingDimensions
from ..layouts.factory import get_layout, LayoutName, MissingLayout, LAYOUT_MAP


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

    def process_display(self, name: str, tokens: list[Token], important: bool) -> None:
        for token in tokens:
            name, value, _, _, location, _ = token

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

    def _process_scalar(self, name: str, tokens: list[Token]) -> None:
        if not tokens:
            return
        if len(tokens) == 1:
            setattr(self.styles, name, Scalar.parse(tokens[0].value))
        else:
            self.error(name, tokens[0], "a single scalar is expected")

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

    def process_visibility(
        self, name: str, tokens: list[Token], important: bool
    ) -> None:
        for token in tokens:
            name, value, _, _, location, _ = token
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
        setattr(
            self.styles,
            f"_rule_{name}",
            Spacing.unpack(cast(SpacingDimensions, tuple(space))),
        )

    def process_padding(self, name: str, tokens: list[Token], important: bool) -> None:
        self._process_space(name, tokens)

    def process_margin(self, name: str, tokens: list[Token], important: bool) -> None:
        self._process_space(name, tokens)

    def _parse_border(self, name: str, tokens: list[Token]) -> tuple[str, Style]:
        style = Style()
        border_type = "solid"
        style_tokens: list[str] = []
        append = style_tokens.append
        for token in tokens:
            token_name, value, _, _, _, _ = token
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
        setattr(self.styles, f"_rule_border_{edge}", border)

    def process_border(self, name: str, tokens: list[Token], important: bool) -> None:
        border = self._parse_border("border", tokens)
        styles = self.styles
        styles._rule_border_top = styles._rule_border_right = border
        styles._rule_border_bottom = styles._rule_border_left = border

    def process_border_top(
        self, name: str, tokens: list[Token], important: bool
    ) -> None:
        self._process_border("top", name, tokens)

    def process_border_right(
        self, name: str, tokens: list[Token], important: bool
    ) -> None:
        self._process_border("right", name, tokens)

    def process_border_bottom(
        self, name: str, tokens: list[Token], important: bool
    ) -> None:
        self._process_border("bottom", name, tokens)

    def process_border_left(
        self, name: str, tokens: list[Token], important: bool
    ) -> None:
        self._process_border("left", name, tokens)

    def _process_outline(self, edge: str, name: str, tokens: list[Token]) -> None:
        border = self._parse_border("outline", tokens)
        setattr(self.styles, f"_rule_outline_{edge}", border)

    def process_outline(self, name: str, tokens: list[Token], important: bool) -> None:
        border = self._parse_border("outline", tokens)
        styles = self.styles
        styles._rule_outline_top = styles._rule_outline_right = border
        styles._rule_outline_bottom = styles._rule_outline_left = border

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
            self.styles._rule_offset = ScalarOffset(scalar_x, scalar_y)

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
            self.styles._rule_offset = ScalarOffset(x, y)

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
            self.styles._rule_offset = ScalarOffset(x, y)

    def process_layout(self, name: str, tokens: list[Token], important: bool) -> None:
        if tokens:
            if len(tokens) != 1:
                self.error(name, tokens[0], "unexpected tokens in declaration")
            else:
                value = tokens[0].value
                layout_name = cast(LayoutName, value)
                try:
                    self.styles._rule_layout = get_layout(layout_name)
                except MissingLayout:
                    self.error(
                        name,
                        tokens[0],
                        f"invalid value for layout (received {value!r}, expected {friendly_list(LAYOUT_MAP.keys())})",
                    )

    def process_text(self, name: str, tokens: list[Token], important: bool) -> None:
        style_definition = " ".join(token.value for token in tokens)

        # If every token in the value is a referenced by the same variable,
        # we can display the variable name before the style definition.
        # TODO: Factor this out to apply it to other properties too.
        unique_references = {t.referenced_by for t in tokens if t.referenced_by}
        if tokens and tokens[0].referenced_by and len(unique_references) == 1:
            variable_prefix = f"${tokens[0].referenced_by.name}="
        else:
            variable_prefix = ""

        try:
            style = Style.parse(style_definition)
            self.styles.text = style
        except Exception as error:
            message = f"property 'text' has invalid value {variable_prefix}{style_definition!r}; {error}"
            self.error(name, tokens[0], message)
        if important:
            self.styles.important.update(
                {"text_style", "text_background", "text_color"}
            )

    def process_text_color(
        self, name: str, tokens: list[Token], important: bool
    ) -> None:
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

    def process_text_background(
        self, name: str, tokens: list[Token], important: bool
    ) -> None:
        for token in tokens:
            if token.name in ("color", "token"):
                try:
                    self.styles._rule_text_background = Color.parse(token.value)
                except Exception as error:
                    self.error(
                        name, token, f"failed to parse color {token.value!r}; {error}"
                    )
            else:
                self.error(
                    name, token, f"unexpected token {token.value!r} in declaration"
                )

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
        self.styles._rule_dock = tokens[0].value if tokens else ""

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
        self.styles._rule_docks = tuple(docks + [DockGroup("_default", "top", 0)])

    def process_layer(self, name: str, tokens: list[Token], important: bool) -> None:
        if len(tokens) > 1:
            self.error(name, tokens[1], f"unexpected tokens in dock-edge declaration")
        self.styles._rule_layer = tokens[0].value

    def process_layers(self, name: str, tokens: list[Token], important: bool) -> None:
        layers: list[str] = []
        for token in tokens:
            if token.name != "token":
                self.error(name, token, "{token.name} not expected here")
            layers.append(token.value)
        self.styles._rule_layers = tuple(layers)

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

        self.styles._rule_transitions = transitions
