from contextlib import nullcontext as does_not_raise

import pytest

from textual.color import Color
from textual.css.stylesheet import CssSource, Stylesheet, StylesheetParseError
from textual.css.tokenizer import TokenError
from textual.dom import DOMNode
from textual.geometry import Spacing
from textual.widget import Widget


def _make_user_stylesheet(css: str) -> Stylesheet:
    stylesheet = Stylesheet()
    stylesheet.source["test.tcss"] = CssSource(css, is_defaults=False)
    stylesheet.parse()
    return stylesheet


def test_stylesheet_apply_highest_specificity_wins():
    """#ids have higher specificity than .classes"""
    css = "#id {color: red;} .class {color: blue;}"
    stylesheet = _make_user_stylesheet(css)
    node = DOMNode(classes="class", id="id")
    stylesheet.apply(node)

    assert node.styles.color == Color(255, 0, 0)


def test_stylesheet_apply_doesnt_override_defaults():
    css = "#id {color: red;}"
    stylesheet = _make_user_stylesheet(css)
    node = DOMNode(id="id")
    stylesheet.apply(node)

    assert node.styles.margin == Spacing.all(0)
    assert node.styles.box_sizing == "border-box"


def test_stylesheet_apply_highest_specificity_wins_multiple_classes():
    """When we use two selectors containing only classes, then the selector
    `.b.c` has greater specificity than the selector `.a`"""
    css = ".b.c {background: blue;} .a {background: red; color: lime;}"
    stylesheet = _make_user_stylesheet(css)
    node = DOMNode(classes="a b c")
    stylesheet.apply(node)

    assert node.styles.background == Color(0, 0, 255)
    assert node.styles.color == Color(0, 255, 0)


def test_stylesheet_many_classes_dont_overrule_id():
    """#id is further to the left in the specificity tuple than class, and
    a selector containing multiple classes cannot take priority over even a
    single class."""
    css = "#id {color: red;} .a.b.c.d {color: blue;}"
    stylesheet = _make_user_stylesheet(css)
    node = DOMNode(classes="a b c d", id="id")
    stylesheet.apply(node)

    assert node.styles.color == Color(255, 0, 0)


def test_stylesheet_last_rule_wins_when_same_rule_twice_in_one_ruleset():
    css = "#id {color: red; color: blue;}"
    stylesheet = _make_user_stylesheet(css)
    node = DOMNode(id="id")
    stylesheet.apply(node)

    assert node.styles.color == Color(0, 0, 255)


def test_stylesheet_rulesets_merged_for_duplicate_selectors():
    css = "#id {color: red; background: lime;} #id {color:blue;}"
    stylesheet = _make_user_stylesheet(css)
    node = DOMNode(id="id")
    stylesheet.apply(node)

    assert node.styles.color == Color(0, 0, 255)
    assert node.styles.background == Color(0, 255, 0)


def test_stylesheet_apply_takes_final_rule_in_specificity_clash():
    """.a and .b both contain background and have same specificity, so .b wins
    since it was declared last - the background should be blue."""
    css = ".a {background: red; color: lime;} .b {background: blue;}"
    stylesheet = _make_user_stylesheet(css)
    node = DOMNode(classes="a b", id="c")
    stylesheet.apply(node)

    assert node.styles.color == Color(0, 255, 0)  # color: lime
    assert node.styles.background == Color(0, 0, 255)  # background: blue


def test_stylesheet_apply_empty_rulesets():
    """Ensure that we don't crash when working with empty rulesets"""
    css = ".a {} .b {}"
    stylesheet = _make_user_stylesheet(css)
    node = DOMNode(classes="a b")
    stylesheet.apply(node)


def test_stylesheet_apply_user_css_over_widget_css():
    user_css = ".a {color: red; tint: yellow;}"

    class MyWidget(Widget):
        DEFAULT_CSS = ".a {color: blue !important; background: lime;}"

    node = MyWidget()
    node.add_class("a")

    stylesheet = _make_user_stylesheet(user_css)
    stylesheet.add_source(
        MyWidget.DEFAULT_CSS, "widget.py:MyWidget", is_default_css=True
    )
    stylesheet.apply(node)

    # The node is red because user CSS overrides Widget.DEFAULT_CSS
    assert node.styles.color == Color(255, 0, 0)
    # The background colour defined in the Widget still applies, since user CSS doesn't override it
    assert node.styles.background == Color(0, 255, 0)
    # As expected, the tint colour is yellow, since there's no competition between user or widget CSS
    assert node.styles.tint == Color(255, 255, 0)


@pytest.mark.parametrize(
    "css_value,expectation,expected_color",
    [
        # Valid values:
        ["transparent", does_not_raise(), Color(0, 0, 0, 0)],
        ["ansi_red", does_not_raise(), Color(128, 0, 0, ansi=1)],
        ["ansi_bright_magenta", does_not_raise(), Color(255, 0, 255, ansi=13)],
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
        ["()", pytest.raises(TokenError), None],  # invalid tokens
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
        ["ofset-x", "offset-x"],
        ["ofst_y", "offset-y"],
        ["colr", "color"],
        ["colour", "color"],
        ["wdth", "width"],
        ["wth", "width"],
        ["wh", None],
        ["xkcd", None],
    ],
)
def test_did_you_mean_for_css_property_names(
    css_property_name: str, expected_property_name_suggestion
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

    stylesheet.add_source(css)
    with pytest.raises(StylesheetParseError) as err:
        stylesheet.parse()

    _, help_text = err.value.errors.rules[0].errors[0]  # type: Any, HelpText
    displayed_css_property_name = css_property_name.replace("_", "-")
    expected_summary = f"Invalid CSS property {displayed_css_property_name!r}"
    if expected_property_name_suggestion:
        expected_summary += f". Did you mean '{expected_property_name_suggestion}'?"
    assert help_text.summary == expected_summary


@pytest.mark.parametrize(
    "css_property_name,expected_property_name_suggestion",
    [
        ["backgroundu", "background"],
        ["bckgroundu", "background"],
        ["ofset-x", "offset-x"],
        ["ofst_y", "offset-y"],
        ["colr", "color"],
        ["colour", "color"],
        ["wdth", "width"],
        ["wth", "width"],
        ["wh", None],
        ["xkcd", None],
    ],
)
def test_did_you_mean_for_property_names_in_nested_css(
    css_property_name: str, expected_property_name_suggestion: "str | None"
) -> None:
    """Test that we get nice errors with mistyped declaractions in nested CSS.

    When implementing pseudo-class support in nested TCSS
    (https://github.com/Textualize/textual/issues/4039), the first iterations didn't
    preserve this so we add these tests to make sure we don't take this feature away
    unintentionally.
    """
    stylesheet = Stylesheet()
    css = """
    Screen {
        * {
            border: blue;
            ${PROPERTY}: red;
        }
    }
    """.replace(
        "${PROPERTY}", css_property_name
    )

    stylesheet.add_source(css)
    with pytest.raises(StylesheetParseError) as err:
        stylesheet.parse()

    _, help_text = err.value.errors.rules[1].errors[0]
    displayed_css_property_name = css_property_name.replace("_", "-")
    expected_summary = f"Invalid CSS property {displayed_css_property_name!r}"
    if expected_property_name_suggestion:
        expected_summary += f". Did you mean '{expected_property_name_suggestion}'?"
    assert help_text.summary == expected_summary


@pytest.mark.parametrize(
    "css_property_name,css_property_value,expected_color_suggestion",
    [
        ["color", "blu", "blue"],
        ["background", "chartruse", "chartreuse"],
        ["tint", "ansi_whi", "ansi_white"],
        ["scrollbar-color", "transprnt", "transparent"],
        ["color", "xkcd", None],
    ],
)
def test_did_you_mean_for_color_names(
    css_property_name: str, css_property_value: str, expected_color_suggestion
):
    stylesheet = Stylesheet()
    css = """
    * {
      border: blue;
      ${PROPERTY}: ${VALUE};
    }
    """.replace(
        "${PROPERTY}", css_property_name
    ).replace(
        "${VALUE}", css_property_value
    )

    stylesheet.add_source(css)
    with pytest.raises(StylesheetParseError) as err:
        stylesheet.parse()

    _, help_text = err.value.errors.rules[0].errors[0]  # type: Any, HelpText
    displayed_css_property_name = css_property_name.replace("_", "-")
    expected_error_summary = f"Invalid value ({css_property_value!r}) for the [i]{displayed_css_property_name}[/] property"

    if expected_color_suggestion is not None:
        expected_error_summary += f". Did you mean '{expected_color_suggestion}'?"

    assert help_text.summary == expected_error_summary
