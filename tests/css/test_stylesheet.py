from contextlib import nullcontext as does_not_raise
import pytest

from textual.color import Color
from textual.css.stylesheet import Stylesheet, StylesheetParseError
from textual.css.tokenizer import TokenizeError


@pytest.mark.parametrize(
    "css_value,expectation,expected_color",
    [
        # Valid values:
        ["red", does_not_raise(), Color(128, 0, 0)],
        ["dark_cyan", does_not_raise(), Color(0, 175, 135)],
        ["medium_turquoise", does_not_raise(), Color(95, 215, 215)],
        ["turquoise4", does_not_raise(), Color(0, 135, 135)],
        ["#ffcc00", does_not_raise(), Color(255, 204, 0)],
        ["#ffcc0033", does_not_raise(), Color(255, 204, 0, 0.2)],
        ["rgb(200,90,30)", does_not_raise(), Color(200, 90, 30)],
        ["rgba(200,90,30,0.3)", does_not_raise(), Color(200, 90, 30, 0.3)],
        # Some invalid ones:
        ["coffee", pytest.raises(StylesheetParseError), None],  # invalid color name
        ["turquoise10", pytest.raises(StylesheetParseError), None],
        ["turquoise 4", pytest.raises(StylesheetParseError), None],  # space in it
        ["1", pytest.raises(StylesheetParseError), None],  # invalid value
        ["()", pytest.raises(TokenizeError), None],  # invalid tokens
        # TODO: implement hex colors with 3 chars? @link https://devdocs.io/css/color_value
        ["#09f", pytest.raises(TokenizeError), None],
        # TODO: allow spaces in rgb/rgba expressions?
        ["rgb(200, 90, 30)", pytest.raises(TokenizeError), None],
        ["rgba(200,90,30, 0.4)", pytest.raises(TokenizeError), None],
    ],
)
def test_color_property_parsing(css_value, expectation, expected_color):
    stylesheet = Stylesheet()
    css = """
    * {
      background: ${COLOR};
    }
    """.replace(
        "${COLOR}", css_value
    )

    with expectation:
        stylesheet.parse(css)

    if expected_color:
        css_rule = stylesheet.rules[0]
        assert css_rule.styles.background == expected_color
