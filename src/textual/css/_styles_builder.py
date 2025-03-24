from __future__ import annotations

from typing import Iterable, NoReturn, cast

import rich.repr

from textual._border import BorderValue, normalize_border_value
from textual._cells import cell_len
from textual._duration import _duration_as_seconds
from textual._easing import EASING
from textual.color import TRANSPARENT, Color, ColorParseError
from textual.css._error_tools import friendly_list
from textual.css._help_renderables import HelpText
from textual.css._help_text import (
    align_help_text,
    border_property_help_text,
    color_property_help_text,
    dock_property_help_text,
    fractional_property_help_text,
    integer_help_text,
    keyline_help_text,
    layout_property_help_text,
    offset_property_help_text,
    offset_single_axis_help_text,
    position_help_text,
    property_invalid_value_help_text,
    scalar_help_text,
    scrollbar_size_property_help_text,
    scrollbar_size_single_axis_help_text,
    spacing_invalid_value_help_text,
    spacing_wrong_number_of_values_help_text,
    split_property_help_text,
    string_enum_help_text,
    style_flags_property_help_text,
    table_rows_or_columns_help_text,
    text_align_help_text,
)
from textual.css.constants import (
    HATCHES,
    VALID_ALIGN_HORIZONTAL,
    VALID_ALIGN_VERTICAL,
    VALID_BORDER,
    VALID_BOX_SIZING,
    VALID_CONSTRAIN,
    VALID_DISPLAY,
    VALID_EDGE,
    VALID_HATCH,
    VALID_KEYLINE,
    VALID_OVERFLOW,
    VALID_OVERLAY,
    VALID_POSITION,
    VALID_SCROLLBAR_GUTTER,
    VALID_STYLE_FLAGS,
    VALID_TEXT_ALIGN,
    VALID_TEXT_OVERFLOW,
    VALID_TEXT_WRAP,
    VALID_VISIBILITY,
)
from textual.css.errors import DeclarationError, StyleValueError
from textual.css.model import Declaration
from textual.css.scalar import (
    Scalar,
    ScalarError,
    ScalarOffset,
    ScalarParseError,
    Unit,
    percentage_string_to_float,
)
from textual.css.styles import Styles
from textual.css.tokenize import Token
from textual.css.transition import Transition
from textual.css.types import (
    BoxSizing,
    Display,
    EdgeType,
    Overflow,
    TextOverflow,
    TextWrap,
    Visibility,
)
from textual.geometry import Spacing, SpacingDimensions, clamp
from textual.suggestions import get_suggestion


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

    def error(self, name: str, token: Token, message: str | HelpText) -> NoReturn:
        raise DeclarationError(name, token, message)

    def add_declaration(self, declaration: Declaration) -> None:
        if not declaration.name:
            return
        rule_name = declaration.name.replace("-", "_")

        if not declaration.tokens:
            self.error(
                rule_name,
                declaration.token,
                f"Missing property value for '{declaration.name}:'",
            )

        process_method = getattr(self, f"process_{rule_name}", None)

        if process_method is None:
            suggested_property_name = self._get_suggested_property_name_for_rule(
                declaration.name
            )
            self.error(
                declaration.name,
                declaration.token,
                property_invalid_value_help_text(
                    declaration.name,
                    "css",
                    suggested_property_name=suggested_property_name,
                ),
            )

        tokens = declaration.tokens

        important = tokens[-1].name == "important"
        if important:
            tokens = tokens[:-1]
            self.styles.important.add(rule_name)

        # Check for special token(s)
        if tokens[0].name == "token":
            value = tokens[0].value
            if value == "initial":
                self.styles._rules[rule_name] = None
                return
        try:
            process_method(declaration.name, tokens)
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
        results: list[str] = []
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
            name: Name of declaration.
            tokens: Tokens from parser.
            valid_values: A set of valid values.

        Returns:
            True if the value is valid or False if it is invalid (also generates an error)
        """

        if len(tokens) != 1:
            self.error(
                name,
                tokens[0],
                string_enum_help_text(
                    name, valid_values=list(valid_values), context="css"
                ),
            )

        token = tokens[0]
        token_name, value, _, _, location, _ = token
        if token_name != "token":
            self.error(
                name,
                token,
                string_enum_help_text(
                    name, valid_values=list(valid_values), context="css"
                ),
            )
        if value not in valid_values:
            self.error(
                name,
                token,
                string_enum_help_text(
                    name, valid_values=list(valid_values), context="css"
                ),
            )
        return value

    def process_display(self, name: str, tokens: list[Token]) -> None:
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
                        string_enum_help_text(
                            "display", valid_values=list(VALID_DISPLAY), context="css"
                        ),
                    )
            else:
                self.error(
                    name,
                    token,
                    string_enum_help_text(
                        "display", valid_values=list(VALID_DISPLAY), context="css"
                    ),
                )

    def _process_scalar(self, name: str, tokens: list[Token]) -> None:
        def scalar_error():
            self.error(
                name, tokens[0], scalar_help_text(property_name=name, context="css")
            )

        if not tokens:
            return
        if len(tokens) == 1:
            try:
                self.styles._rules[name.replace("-", "_")] = Scalar.parse(  # type: ignore
                    tokens[0].value
                )
            except ScalarParseError:
                scalar_error()
        else:
            scalar_error()

    def _distribute_importance(self, prefix: str, suffixes: tuple[str, ...]) -> None:
        """Distribute importance amongst all aspects of the given style.

        Args:
            prefix: The prefix of the style.
            suffixes: The suffixes to distribute amongst.

        A number of styles can be set with the 'prefix' of the style,
        providing the values as a series of parameters; or they can be set
        with specific suffixes. Think `border` vs `border-left`, etc. This
        method is used to ensure that if the former is set, `!important` is
        distributed amongst all the suffixes.
        """
        if prefix in self.styles.important:
            self.styles.important.remove(prefix)
            self.styles.important.update(f"{prefix}_{suffix}" for suffix in suffixes)

    def process_box_sizing(self, name: str, tokens: list[Token]) -> None:
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
                        string_enum_help_text(
                            "box-sizing",
                            valid_values=list(VALID_BOX_SIZING),
                            context="css",
                        ),
                    )
            else:
                self.error(
                    name,
                    token,
                    string_enum_help_text(
                        "box-sizing", valid_values=list(VALID_BOX_SIZING), context="css"
                    ),
                )

    def process_width(self, name: str, tokens: list[Token]) -> None:
        self._process_scalar(name, tokens)

    def process_height(self, name: str, tokens: list[Token]) -> None:
        self._process_scalar(name, tokens)

    def process_min_width(self, name: str, tokens: list[Token]) -> None:
        self._process_scalar(name, tokens)

    def process_min_height(self, name: str, tokens: list[Token]) -> None:
        self._process_scalar(name, tokens)

    def process_max_width(self, name: str, tokens: list[Token]) -> None:
        self._process_scalar(name, tokens)

    def process_max_height(self, name: str, tokens: list[Token]) -> None:
        self._process_scalar(name, tokens)

    def process_overflow(self, name: str, tokens: list[Token]) -> None:
        rules = self.styles._rules
        overflow_x, overflow_y = self._process_enum_multiple(
            name, tokens, VALID_OVERFLOW, 2
        )
        rules["overflow_x"] = cast(Overflow, overflow_x)
        rules["overflow_y"] = cast(Overflow, overflow_y)
        self._distribute_importance("overflow", ("x", "y"))

    def process_overflow_x(self, name: str, tokens: list[Token]) -> None:
        self.styles._rules["overflow_x"] = cast(
            Overflow, self._process_enum(name, tokens, VALID_OVERFLOW)
        )

    def process_overflow_y(self, name: str, tokens: list[Token]) -> None:
        self.styles._rules["overflow_y"] = cast(
            Overflow, self._process_enum(name, tokens, VALID_OVERFLOW)
        )

    def process_visibility(self, name: str, tokens: list[Token]) -> None:
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
                        string_enum_help_text(
                            "visibility",
                            valid_values=list(VALID_VISIBILITY),
                            context="css",
                        ),
                    )
            else:
                string_enum_help_text(
                    "visibility", valid_values=list(VALID_VISIBILITY), context="css"
                )

    def process_text_wrap(self, name: str, tokens: list[Token]) -> None:
        for token in tokens:
            name, value, _, _, location, _ = token
            if name == "token":
                value = value.lower()
                if value in VALID_TEXT_WRAP:
                    self.styles._rules["text_wrap"] = cast(TextWrap, value)
                else:
                    self.error(
                        name,
                        token,
                        string_enum_help_text(
                            "text-wrap",
                            valid_values=list(VALID_TEXT_WRAP),
                            context="css",
                        ),
                    )
            else:
                string_enum_help_text(
                    "text-wrap", valid_values=list(VALID_TEXT_WRAP), context="css"
                )

    def process_text_overflow(self, name: str, tokens: list[Token]) -> None:
        for token in tokens:
            name, value, _, _, location, _ = token
            if name == "token":
                value = value.lower()
                if value in VALID_TEXT_OVERFLOW:
                    self.styles._rules["text_overflow"] = cast(TextOverflow, value)
                else:
                    self.error(
                        name,
                        token,
                        string_enum_help_text(
                            "text-overflow",
                            valid_values=list(VALID_TEXT_OVERFLOW),
                            context="css",
                        ),
                    )
            else:
                string_enum_help_text(
                    "text-overflow",
                    valid_values=list(VALID_TEXT_OVERFLOW),
                    context="css",
                )

    def _process_fractional(self, name: str, tokens: list[Token]) -> None:
        if not tokens:
            return
        token = tokens[0]
        error = False
        if len(tokens) != 1:
            error = True
        else:
            token_name = token.name
            value = token.value
            rule_name = name.replace("-", "_")
            if token_name == "scalar" and value.endswith("%"):
                try:
                    text_opacity = percentage_string_to_float(value)
                    self.styles.set_rule(rule_name, text_opacity)
                except ValueError:
                    error = True
            elif token_name == "number":
                try:
                    text_opacity = clamp(float(value), 0, 1)
                    self.styles.set_rule(rule_name, text_opacity)
                except ValueError:
                    error = True
            else:
                error = True

        if error:
            self.error(name, token, fractional_property_help_text(name, context="css"))

    process_opacity = _process_fractional
    process_text_opacity = _process_fractional

    def _process_space(self, name: str, tokens: list[Token]) -> None:
        space: list[int] = []
        append = space.append
        for token in tokens:
            token_name, value, _, _, _, _ = token
            if token_name == "number":
                try:
                    append(int(value))
                except ValueError:
                    self.error(
                        name,
                        token,
                        spacing_invalid_value_help_text(name, context="css"),
                    )
            else:
                self.error(
                    name, token, spacing_invalid_value_help_text(name, context="css")
                )
        if len(space) not in (1, 2, 4):
            self.error(
                name,
                tokens[0],
                spacing_wrong_number_of_values_help_text(
                    name, num_values_supplied=len(space), context="css"
                ),
            )
        self.styles._rules[name] = Spacing.unpack(cast(SpacingDimensions, tuple(space)))  # type: ignore

    def _process_space_partial(self, name: str, tokens: list[Token]) -> None:
        """Process granular margin / padding declarations."""
        if len(tokens) != 1:
            self.error(
                name, tokens[0], spacing_invalid_value_help_text(name, context="css")
            )

        _EDGE_SPACING_MAP = {"top": 0, "right": 1, "bottom": 2, "left": 3}
        token = tokens[0]
        token_name, value, _, _, _, _ = token
        if token_name == "number":
            space = int(value)
        else:
            self.error(
                name, token, spacing_invalid_value_help_text(name, context="css")
            )
        style_name, _, edge = name.replace("-", "_").partition("_")

        current_spacing = cast(
            "tuple[int, int, int, int]",
            self.styles._rules.get(style_name, (0, 0, 0, 0)),
        )

        spacing_list = list(current_spacing)
        spacing_list[_EDGE_SPACING_MAP[edge]] = space

        self.styles._rules[style_name] = Spacing(*spacing_list)  # type: ignore

    process_padding = _process_space
    process_margin = _process_space

    process_margin_top = _process_space_partial
    process_margin_right = _process_space_partial
    process_margin_bottom = _process_space_partial
    process_margin_left = _process_space_partial

    process_padding_top = _process_space_partial
    process_padding_right = _process_space_partial
    process_padding_bottom = _process_space_partial
    process_padding_left = _process_space_partial

    def _parse_border(self, name: str, tokens: list[Token]) -> BorderValue:
        border_type: EdgeType = "solid"
        border_color = Color(0, 255, 0)
        border_alpha: float | None = None

        def border_value_error():
            self.error(name, token, border_property_help_text(name, context="css"))

        for token in tokens:
            token_name, value, _, _, _, _ = token
            if token_name == "token":
                if value in VALID_BORDER:
                    border_type = value  # type: ignore
                else:
                    try:
                        border_color = Color.parse(value)
                    except ColorParseError:
                        border_value_error()

            elif token_name == "color":
                try:
                    border_color = Color.parse(value)
                except ColorParseError:
                    border_value_error()

            elif token_name == "scalar":
                alpha_scalar = Scalar.parse(token.value)
                if alpha_scalar.unit != Unit.PERCENT:
                    self.error(name, token, "alpha must be given as a percentage.")
                border_alpha = alpha_scalar.value / 100.0

            else:
                border_value_error()

        if border_alpha is not None:
            border_color = border_color.multiply_alpha(border_alpha)

        return normalize_border_value((border_type, border_color))

    def _process_border_edge(self, edge: str, name: str, tokens: list[Token]) -> None:
        border = self._parse_border(name, tokens)
        self.styles._rules[f"border_{edge}"] = border  # type: ignore

    def process_border(self, name: str, tokens: list[Token]) -> None:
        border = self._parse_border(name, tokens)
        rules = self.styles._rules
        rules["border_top"] = rules["border_right"] = border
        rules["border_bottom"] = rules["border_left"] = border
        self._distribute_importance("border", ("top", "left", "bottom", "right"))

    def process_border_top(self, name: str, tokens: list[Token]) -> None:
        self._process_border_edge("top", name, tokens)

    def process_border_right(self, name: str, tokens: list[Token]) -> None:
        self._process_border_edge("right", name, tokens)

    def process_border_bottom(self, name: str, tokens: list[Token]) -> None:
        self._process_border_edge("bottom", name, tokens)

    def process_border_left(self, name: str, tokens: list[Token]) -> None:
        self._process_border_edge("left", name, tokens)

    def _process_outline(self, edge: str, name: str, tokens: list[Token]) -> None:
        border = self._parse_border(name, tokens)
        self.styles._rules[f"outline_{edge}"] = border  # type: ignore

    def process_outline(self, name: str, tokens: list[Token]) -> None:
        border = self._parse_border(name, tokens)
        rules = self.styles._rules
        rules["outline_top"] = rules["outline_right"] = border
        rules["outline_bottom"] = rules["outline_left"] = border
        self._distribute_importance("outline", ("top", "left", "bottom", "right"))

    def process_outline_top(self, name: str, tokens: list[Token]) -> None:
        self._process_outline("top", name, tokens)

    def process_outline_right(self, name: str, tokens: list[Token]) -> None:
        self._process_outline("right", name, tokens)

    def process_outline_bottom(self, name: str, tokens: list[Token]) -> None:
        self._process_outline("bottom", name, tokens)

    def process_outline_left(self, name: str, tokens: list[Token]) -> None:
        self._process_outline("left", name, tokens)

    def process_keyline(self, name: str, tokens: list[Token]) -> None:
        if not tokens:
            return
        if len(tokens) > 3:
            self.error(name, tokens[0], keyline_help_text())
        keyline_style = "none"
        keyline_color = Color.parse("green")
        keyline_alpha = 1.0
        for token in tokens:
            if token.name == "color":
                try:
                    keyline_color = Color.parse(token.value)
                except Exception as error:
                    self.error(
                        name,
                        token,
                        color_property_help_text(
                            name, context="css", error=error, value=token.value
                        ),
                    )
            elif token.name == "token":
                try:
                    keyline_color = Color.parse(token.value)
                except Exception:
                    keyline_style = token.value
                    if keyline_style not in VALID_KEYLINE:
                        self.error(name, token, keyline_help_text())

            elif token.name == "scalar":
                alpha_scalar = Scalar.parse(token.value)
                if alpha_scalar.unit != Unit.PERCENT:
                    self.error(name, token, "alpha must be given as a percentage.")
                keyline_alpha = alpha_scalar.value / 100.0

        self.styles._rules["keyline"] = (
            keyline_style,
            keyline_color.multiply_alpha(keyline_alpha),
        )

    def process_offset(self, name: str, tokens: list[Token]) -> None:
        def offset_error(name: str, token: Token) -> None:
            self.error(name, token, offset_property_help_text(context="css"))

        if not tokens:
            return
        if len(tokens) != 2:
            offset_error(name, tokens[0])
        else:
            token1, token2 = tokens

            if token1.name not in ("scalar", "number"):
                offset_error(name, token1)
            if token2.name not in ("scalar", "number"):
                offset_error(name, token2)

            scalar_x = Scalar.parse(token1.value, Unit.WIDTH)
            scalar_y = Scalar.parse(token2.value, Unit.HEIGHT)
            self.styles._rules["offset"] = ScalarOffset(scalar_x, scalar_y)

    def process_offset_x(self, name: str, tokens: list[Token]) -> None:
        if not tokens:
            return
        if len(tokens) != 1:
            self.error(name, tokens[0], offset_single_axis_help_text(name))
        else:
            token = tokens[0]
            if token.name not in ("scalar", "number"):
                self.error(name, token, offset_single_axis_help_text(name))
            x = Scalar.parse(token.value, Unit.WIDTH)
            y = self.styles.offset.y
            self.styles._rules["offset"] = ScalarOffset(x, y)

    def process_offset_y(self, name: str, tokens: list[Token]) -> None:
        if not tokens:
            return
        if len(tokens) != 1:
            self.error(name, tokens[0], offset_single_axis_help_text(name))
        else:
            token = tokens[0]
            if token.name not in ("scalar", "number"):
                self.error(name, token, offset_single_axis_help_text(name))
            y = Scalar.parse(token.value, Unit.HEIGHT)
            x = self.styles.offset.x
            self.styles._rules["offset"] = ScalarOffset(x, y)

    def process_position(self, name: str, tokens: list[Token]):
        if not tokens:
            return
        if len(tokens) != 1:
            self.error(name, tokens[0], offset_single_axis_help_text(name))
        else:
            token = tokens[0]
            if token.value not in VALID_POSITION:
                self.error(name, tokens[0], position_help_text(name))
            self.styles._rules["position"] = token.value

    def process_layout(self, name: str, tokens: list[Token]) -> None:
        from textual.layouts.factory import MissingLayout, get_layout

        if tokens:
            if len(tokens) != 1:
                self.error(
                    name, tokens[0], layout_property_help_text(name, context="css")
                )
            else:
                value = tokens[0].value
                layout_name = value
                try:
                    self.styles._rules["layout"] = get_layout(layout_name)
                except MissingLayout:
                    self.error(
                        name,
                        tokens[0],
                        layout_property_help_text(name, context="css"),
                    )

    def process_color(self, name: str, tokens: list[Token]) -> None:
        """Processes a simple color declaration."""
        name = name.replace("-", "_")

        color: Color | None = None
        alpha: float | None = None

        self.styles._rules[f"auto_{name}"] = False  # type: ignore
        for token in tokens:
            if (
                "background" not in name
                and token.name == "token"
                and token.value == "auto"
            ):
                self.styles._rules[f"auto_{name}"] = True  # type: ignore
            elif token.name == "scalar":
                alpha_scalar = Scalar.parse(token.value)
                if alpha_scalar.unit != Unit.PERCENT:
                    self.error(name, token, "alpha must be given as a percentage.")
                alpha = alpha_scalar.value / 100.0

            elif token.name in ("color", "token"):
                try:
                    color = Color.parse(token.value)
                except Exception as error:
                    self.error(
                        name,
                        token,
                        color_property_help_text(
                            name, context="css", error=error, value=token.value
                        ),
                    )
            else:
                self.error(
                    name,
                    token,
                    color_property_help_text(name, context="css", value=token.value),
                )

        if color is not None or alpha is not None:
            if alpha is not None:
                color = (color or Color(255, 255, 255)).multiply_alpha(alpha)
            self.styles._rules[name] = color  # type: ignore

    process_tint = process_color
    process_background = process_color
    process_background_tint = process_color
    process_scrollbar_color = process_color
    process_scrollbar_color_hover = process_color
    process_scrollbar_color_active = process_color
    process_scrollbar_corner_color = process_color
    process_scrollbar_background = process_color
    process_scrollbar_background_hover = process_color
    process_scrollbar_background_active = process_color

    process_link_color = process_color
    process_link_background = process_color
    process_link_color_hover = process_color
    process_link_background_hover = process_color

    process_border_title_color = process_color
    process_border_title_background = process_color
    process_border_subtitle_color = process_color
    process_border_subtitle_background = process_color

    def process_text_style(self, name: str, tokens: list[Token]) -> None:
        for token in tokens:
            value = token.value
            if value not in VALID_STYLE_FLAGS:
                self.error(
                    name,
                    token,
                    style_flags_property_help_text(name, value, context="css"),
                )

        style_definition = " ".join(token.value for token in tokens)
        self.styles._rules[name.replace("-", "_")] = style_definition  # type: ignore

    process_link_style = process_text_style
    process_link_style_hover = process_text_style

    process_border_title_style = process_text_style
    process_border_subtitle_style = process_text_style

    def process_text_align(self, name: str, tokens: list[Token]) -> None:
        """Process a text-align declaration"""
        if not tokens:
            return

        if len(tokens) > 1 or tokens[0].value not in VALID_TEXT_ALIGN:
            self.error(
                name,
                tokens[0],
                text_align_help_text(),
            )

        self.styles._rules["text_align"] = tokens[0].value  # type: ignore

    def process_dock(self, name: str, tokens: list[Token]) -> None:
        if not tokens:
            return

        if len(tokens) > 1 or tokens[0].value not in VALID_EDGE:
            self.error(
                name,
                tokens[0],
                dock_property_help_text(name, context="css"),
            )

        dock_value = tokens[0].value
        self.styles._rules["dock"] = dock_value

    def process_split(self, name: str, tokens: list[Token]) -> None:
        if not tokens:
            return

        if len(tokens) > 1 or tokens[0].value not in VALID_EDGE:
            self.error(
                name,
                tokens[0],
                split_property_help_text(name, context="css"),
            )

        split_value = tokens[0].value
        self.styles._rules["split"] = split_value

    def process_layer(self, name: str, tokens: list[Token]) -> None:
        if len(tokens) > 1:
            self.error(name, tokens[1], "unexpected tokens in dock-edge declaration")
        self.styles._rules["layer"] = tokens[0].value

    def process_layers(self, name: str, tokens: list[Token]) -> None:
        layers: list[str] = []
        for token in tokens:
            if token.name not in {"token", "string"}:
                self.error(name, token, f"{token.name} not expected here")
            layers.append(token.value)
        self.styles._rules["layers"] = tuple(layers)

    def process_transition(self, name: str, tokens: list[Token]) -> None:
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

    def process_align(self, name: str, tokens: list[Token]) -> None:
        def align_error(name, token):
            self.error(name, token, align_help_text())

        if len(tokens) != 2:
            self.error(name, tokens[0], align_help_text())

        token_horizontal = tokens[0]
        token_vertical = tokens[1]

        if token_horizontal.name != "token":
            align_error(name, token_horizontal)
        elif token_horizontal.value not in VALID_ALIGN_HORIZONTAL:
            align_error(name, token_horizontal)

        if token_vertical.name != "token":
            align_error(name, token_vertical)
        elif token_vertical.value not in VALID_ALIGN_VERTICAL:
            align_error(name, token_horizontal)

        name = name.replace("-", "_")
        self.styles._rules[f"{name}_horizontal"] = token_horizontal.value  # type: ignore
        self.styles._rules[f"{name}_vertical"] = token_vertical.value  # type: ignore

        self._distribute_importance(name, ("horizontal", "vertical"))

    def process_align_horizontal(self, name: str, tokens: list[Token]) -> None:
        try:
            value = self._process_enum(name, tokens, VALID_ALIGN_HORIZONTAL)
        except StyleValueError:
            self.error(
                name,
                tokens[0],
                string_enum_help_text(name, VALID_ALIGN_HORIZONTAL, context="css"),
            )
        else:
            self.styles._rules[name.replace("-", "_")] = value  # type: ignore

    def process_align_vertical(self, name: str, tokens: list[Token]) -> None:
        try:
            value = self._process_enum(name, tokens, VALID_ALIGN_VERTICAL)
        except StyleValueError:
            self.error(
                name,
                tokens[0],
                string_enum_help_text(name, VALID_ALIGN_VERTICAL, context="css"),
            )
        else:
            self.styles._rules[name.replace("-", "_")] = value  # type: ignore

    process_content_align = process_align
    process_content_align_horizontal = process_align_horizontal
    process_content_align_vertical = process_align_vertical

    process_border_title_align = process_align_horizontal
    process_border_subtitle_align = process_align_horizontal

    def process_scrollbar_gutter(self, name: str, tokens: list[Token]) -> None:
        try:
            value = self._process_enum(name, tokens, VALID_SCROLLBAR_GUTTER)
        except StyleValueError:
            self.error(
                name,
                tokens[0],
                string_enum_help_text(name, VALID_SCROLLBAR_GUTTER, context="css"),
            )
        else:
            self.styles._rules[name.replace("-", "_")] = value  # type: ignore

    def process_scrollbar_size(self, name: str, tokens: list[Token]) -> None:
        def scrollbar_size_error(name: str, token: Token) -> None:
            self.error(name, token, scrollbar_size_property_help_text(context="css"))

        if not tokens:
            return
        if len(tokens) != 2:
            scrollbar_size_error(name, tokens[0])
        else:
            token1, token2 = tokens

            if token1.name != "number" or not token1.value.isdigit():
                scrollbar_size_error(name, token1)
            if token2.name != "number" or not token2.value.isdigit():
                scrollbar_size_error(name, token2)

            horizontal = int(token1.value)
            vertical = int(token2.value)
            self.styles._rules["scrollbar_size_horizontal"] = horizontal
            self.styles._rules["scrollbar_size_vertical"] = vertical
            self._distribute_importance("scrollbar_size", ("horizontal", "vertical"))

    def process_scrollbar_size_vertical(self, name: str, tokens: list[Token]) -> None:
        if not tokens:
            return
        if len(tokens) != 1:
            self.error(name, tokens[0], scrollbar_size_single_axis_help_text(name))
        else:
            token = tokens[0]
            if token.name != "number" or not token.value.isdigit():
                self.error(name, token, scrollbar_size_single_axis_help_text(name))
            value = int(token.value)
            self.styles._rules["scrollbar_size_vertical"] = value

    def process_scrollbar_size_horizontal(self, name: str, tokens: list[Token]) -> None:
        if not tokens:
            return
        if len(tokens) != 1:
            self.error(name, tokens[0], scrollbar_size_single_axis_help_text(name))
        else:
            token = tokens[0]
            if token.name != "number" or not token.value.isdigit():
                self.error(name, token, scrollbar_size_single_axis_help_text(name))
            value = int(token.value)
            self.styles._rules["scrollbar_size_horizontal"] = value

    def _process_grid_rows_or_columns(self, name: str, tokens: list[Token]) -> None:
        scalars: list[Scalar] = []
        percent_unit = Unit.WIDTH if name == "grid-columns" else Unit.HEIGHT
        for token in tokens:
            if token.name == "number":
                scalars.append(Scalar.from_number(float(token.value)))
            elif token.name == "scalar":
                scalars.append(Scalar.parse(token.value, percent_unit=percent_unit))
            elif token.name == "token" and token.value == "auto":
                scalars.append(Scalar.parse("auto"))
            else:
                self.error(
                    name,
                    token,
                    table_rows_or_columns_help_text(name, token.value, context="css"),
                )
        self.styles._rules[name.replace("-", "_")] = scalars  # type: ignore

    process_grid_rows = _process_grid_rows_or_columns
    process_grid_columns = _process_grid_rows_or_columns

    def _process_integer(self, name: str, tokens: list[Token]) -> None:
        if not tokens:
            return
        if len(tokens) != 1:
            self.error(name, tokens[0], integer_help_text(name))
        else:
            token = tokens[0]
            if token.name != "number" or not token.value.isdigit():
                self.error(name, token, integer_help_text(name))
            value = int(token.value)
            if value == 0:
                self.error(name, token, integer_help_text(name))
            self.styles._rules[name.replace("-", "_")] = value  # type: ignore

    process_grid_gutter_horizontal = _process_integer
    process_grid_gutter_vertical = _process_integer
    process_column_span = _process_integer
    process_row_span = _process_integer
    process_grid_size_columns = _process_integer
    process_grid_size_rows = _process_integer
    process_line_pad = _process_integer

    def process_grid_gutter(self, name: str, tokens: list[Token]) -> None:
        if not tokens:
            return
        if len(tokens) == 1:
            token = tokens[0]
            if token.name != "number":
                self.error(name, token, integer_help_text(name))
            value = max(0, int(token.value))
            self.styles._rules["grid_gutter_horizontal"] = value
            self.styles._rules["grid_gutter_vertical"] = value

        elif len(tokens) == 2:
            token = tokens[0]
            if token.name != "number":
                self.error(name, token, integer_help_text(name))
            value = max(0, int(token.value))
            self.styles._rules["grid_gutter_horizontal"] = value
            token = tokens[1]
            if token.name != "number":
                self.error(name, token, integer_help_text(name))
            value = max(0, int(token.value))
            self.styles._rules["grid_gutter_vertical"] = value

        else:
            self.error(name, tokens[0], "expected two integers here")

    def process_grid_size(self, name: str, tokens: list[Token]) -> None:
        if not tokens:
            return
        if len(tokens) == 1:
            token = tokens[0]
            if token.name != "number":
                self.error(name, token, integer_help_text(name))
            value = max(0, int(token.value))
            self.styles._rules["grid_size_columns"] = value
            self.styles._rules["grid_size_rows"] = 0

        elif len(tokens) == 2:
            token = tokens[0]
            if token.name != "number":
                self.error(name, token, integer_help_text(name))
            value = max(0, int(token.value))
            self.styles._rules["grid_size_columns"] = value
            token = tokens[1]
            if token.name != "number":
                self.error(name, token, integer_help_text(name))
            value = max(0, int(token.value))
            self.styles._rules["grid_size_rows"] = value

        else:
            self.error(name, tokens[0], "expected two integers here")

    def process_overlay(self, name: str, tokens: list[Token]) -> None:
        try:
            value = self._process_enum(name, tokens, VALID_OVERLAY)
        except StyleValueError:
            self.error(
                name,
                tokens[0],
                string_enum_help_text(name, VALID_OVERLAY, context="css"),
            )
        else:
            self.styles._rules[name] = value  # type: ignore

    def process_constrain(self, name: str, tokens: list[Token]) -> None:
        if len(tokens) == 1:
            try:
                value = self._process_enum(name, tokens, VALID_CONSTRAIN)
            except StyleValueError:
                self.error(
                    name,
                    tokens[0],
                    string_enum_help_text(name, VALID_CONSTRAIN, context="css"),
                )
            else:
                self.styles._rules["constrain_x"] = value  # type: ignore
                self.styles._rules["constrain_y"] = value  # type: ignore
        elif len(tokens) == 2:
            constrain_x, constrain_y = self._process_enum_multiple(
                name, tokens, VALID_CONSTRAIN, 2
            )
            self.styles._rules["constrain_x"] = constrain_x  # type: ignore
            self.styles._rules["constrain_y"] = constrain_y  # type: ignore
        else:
            self.error(name, tokens[0], "one or two values expected here")

    def process_constrain_x(self, name: str, tokens: list[Token]) -> None:
        try:
            value = self._process_enum(name, tokens, VALID_CONSTRAIN)
        except StyleValueError:
            self.error(
                name,
                tokens[0],
                string_enum_help_text(name, VALID_CONSTRAIN, context="css"),
            )
        else:
            self.styles._rules[name] = value  # type: ignore

    def process_constrain_y(self, name: str, tokens: list[Token]) -> None:
        try:
            value = self._process_enum(name, tokens, VALID_CONSTRAIN)
        except StyleValueError:
            self.error(
                name,
                tokens[0],
                string_enum_help_text(name, VALID_CONSTRAIN, context="css"),
            )
        else:
            self.styles._rules[name] = value  # type: ignore

    def process_hatch(self, name: str, tokens: list[Token]) -> None:
        if not tokens:
            return
        character: str | None = None
        color = TRANSPARENT
        opacity = 1.0

        if len(tokens) == 1 and tokens[0].value == "none":
            self.styles._rules[name] = "none"
            return

        if len(tokens) not in (2, 3):
            self.error(name, tokens[0], "2 or 3 values expected here")

        character_token, color_token, *opacity_tokens = tokens

        if character_token.name == "token":
            if character_token.value not in VALID_HATCH:
                self.error(
                    name,
                    tokens[0],
                    string_enum_help_text(name, VALID_HATCH, context="css"),
                )
            character = HATCHES[character_token.value]
        elif character_token.name == "string":
            character = character_token.value[1:-1]
            if len(character) != 1:
                self.error(
                    name,
                    character_token,
                    f"Hatch type requires a string of length 1; got {character_token.value}",
                )
            if cell_len(character) != 1:
                self.error(
                    name,
                    character_token,
                    f"Hatch type requires a string with a *cell length* of 1; got {character_token.value}",
                )

        if color_token.name in ("color", "token"):
            try:
                color = Color.parse(color_token.value)
            except Exception as error:
                self.error(
                    name,
                    color_token,
                    color_property_help_text(
                        name, context="css", error=error, value=color_token.value
                    ),
                )
        else:
            self.error(
                name, color_token, f"Expected a color; found {color_token.value!r}"
            )

        if opacity_tokens:
            opacity_token = opacity_tokens[0]
            if opacity_token.name == "scalar":
                opacity_scalar = opacity = Scalar.parse(opacity_token.value)
                if opacity_scalar.unit != Unit.PERCENT:
                    self.error(
                        name,
                        opacity_token,
                        "hatch alpha must be given as a percentage.",
                    )
                opacity = clamp(opacity_scalar.value / 100.0, 0, 1.0)
            else:
                self.error(
                    name,
                    opacity_token,
                    f"expected a percentage here; found {opacity_token.value!r}",
                )

        self.styles._rules[name] = (character or " ", color.multiply_alpha(opacity))

    def _get_suggested_property_name_for_rule(self, rule_name: str) -> str | None:
        """
        Returns a valid CSS property "Python" name, or None if no close matches could be found.

        Args:
            rule_name: An invalid "Python-ised" CSS property (i.e. "offst_x" rather than "offst-x")

        Returns:
            The closest valid "Python-ised" CSS property.
                Returns `None` if no close matches could be found.

        Example: returns "background" for rule_name "bkgrund", "offset_x" for "ofset_x"
        """
        processable_rules_name = [
            attr[8:] for attr in dir(self) if attr.startswith("process_")
        ]
        return get_suggestion(rule_name, processable_rules_name)
