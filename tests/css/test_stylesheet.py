from contextlib import nullcontext as does_not_raise
import pytest

from textual.color import Color
from textual.css.stylesheet import Stylesheet, StylesheetParseError
from textual.css.tokenizer import TokenizeError


@pytest.mark.parametrize(
    "css_value,expectation,expected_color",
    [
        # Valid values:
        ["transparent", does_not_raise(), Color(0, 0, 0, 0)],
        ["ansi_red", does_not_raise(), Color(128, 0, 0)],
        ["ansi_bright_magenta", does_not_raise(), Color(255, 0, 255)],
        ["red", does_not_raise(), Color(255, 0, 0)],
        ["lime", does_not_raise(), Color(0, 255, 0)],
        ["coral", does_not_raise(), Color(255, 127, 80)],
        ["aqua", does_not_raise(), Color(0, 255, 255)],
        ["deepskyblue", does_not_raise(), Color(0, 191, 255)],
        ["rebeccapurple", does_not_raise(), Color(102, 51, 153)],
        ["#ffcc00", does_not_raise(), Color(255, 204, 0)],
        ["#ffcc0033", does_not_raise(), Color(255, 204, 0, 0.2)],
        ["rgb(200,90,30)", does_not_raise(), Color(200, 90, 30)],
        ["rgba(200,90,30,0.3)", does_not_raise(), Color(200, 90, 30, 0.3)],
        # Some invalid ones:
        ["coffee", pytest.raises(StylesheetParseError), None],  # invalid color name
        ["ansi_dark_cyan", pytest.raises(StylesheetParseError), None],
        ["red 4", pytest.raises(StylesheetParseError), None],  # space in it
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
        stylesheet.add_source(css)
        stylesheet.parse()

    if expected_color:
        css_rule = stylesheet.rules[0]
        assert css_rule.styles.background == expected_color


@pytest.mark.parametrize(
    "css_property_name,expected_property_name_suggestion",
    [
        ["backgroundu", "background"],
        ["bckgroundu", "background"],
        ["colr", "color"],
        ["colour", "color"],
        ["wdth", "width"],
        ["wth", "width"],
        ["wh", None],
        ["xkcd", None],
    ],
)
def test_did_you_mean_for_css_property_names(
    css_property_name, expected_property_name_suggestion
):
    stylesheet = Stylesheet()
    css = """
    * {
      border: blue;
      ${PROPERTY}: red;
    }
    """.replace(
        "${PROPERTY}", css_property_name
    )

    with pytest.raises(StylesheetParseError) as err:
        stylesheet.parse(css)

    error_token, error_message = err.value.errors.stylesheet.rules[0].errors[0]
    if expected_property_name_suggestion is None:
        assert "did you mean" not in error_message
    else:
        expected_did_you_mean_error_message = f"unknown declaration '{css_property_name}'; did you mean '{expected_property_name_suggestion}'?"
        assert expected_did_you_mean_error_message == error_message
