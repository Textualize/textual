import pytest

from rich.style import Style

from textual.color import Color
from textual.css.errors import StyleTypeError
from textual.css.styles import Styles, RenderStyles
from textual.dom import DOMNode


def test_styles_reset():
    styles = Styles()
    styles.text_style = "not bold"
    assert styles.text_style == Style(bold=False)
    styles.reset()
    assert styles.text_style is Style.null()


def test_has_rule():
    styles = Styles()
    assert not styles.has_rule("text_style")
    styles.text_style = "bold"
    assert styles.has_rule("text_style")
    styles.text_style = None
    assert not styles.has_rule("text_style")


def test_clear_rule():
    styles = Styles()
    styles.text_style = "bold"
    assert styles.has_rule("text_style")
    styles.clear_rule("text_style")
    assert not styles.has_rule("text_style")


def test_get_rules():
    styles = Styles()
    # Empty rules at start
    assert styles.get_rules() == {}
    styles.text_style = "bold"
    assert styles.get_rules() == {"text_style": Style.parse("bold")}
    styles.display = "none"
    assert styles.get_rules() == {
        "text_style": Style.parse("bold"),
        "display": "none",
    }


def test_set_rule():
    styles = Styles()
    assert styles.get_rules() == {}
    styles.set_rule("text_style", Style.parse("bold"))
    assert styles.get_rules() == {"text_style": Style.parse("bold")}


def test_reset():
    styles = Styles()
    assert styles.get_rules() == {}
    styles.set_rule("text_style", Style.parse("bold"))
    assert styles.get_rules() == {"text_style": Style.parse("bold")}
    styles.reset()
    assert styles.get_rules() == {}


def test_merge():
    styles = Styles()
    styles.set_rule("text_style", Style.parse("bold"))
    styles2 = Styles()
    styles2.set_rule("display", "none")
    styles.merge(styles2)
    assert styles.get_rules() == {
        "text_style": Style.parse("bold"),
        "display": "none",
    }


def test_merge_rules():
    styles = Styles()
    styles.set_rule("text_style", Style.parse("bold"))
    styles.merge_rules({"display": "none"})
    assert styles.get_rules() == {
        "text_style": Style.parse("bold"),
        "display": "none",
    }


def test_render_styles_text():
    """Test inline styles override base styles"""
    base = Styles()
    inline = Styles()
    styles_view = RenderStyles(None, base, inline)

    # Both styles are empty
    assert styles_view.text == Style()

    # Base is bold blue
    base.color = "blue"
    base.text_style = "bold"
    assert styles_view.text == Style.parse("bold blue")

    # Base is bold blue, inline is red
    inline.color = "red"
    assert styles_view.text == Style.parse("bold red")

    # Base is bold yellow, inline is red
    base.color = "yellow"
    assert styles_view.text == Style.parse("bold red")

    # Base is bold blue
    inline.color = None
    assert styles_view.text == Style.parse("bold yellow")


def test_render_styles_border():
    base = Styles()
    inline = Styles()
    styles_view = RenderStyles(None, base, inline)

    base.border_top = ("heavy", "red")
    # Base has border-top: heavy red
    assert styles_view.border_top == ("heavy", Color.parse("red"))

    inline.border_left = ("rounded", "green")
    # Base has border-top heavy red, inline has border-left: rounded green
    assert styles_view.border_top == ("heavy", Color.parse("red"))
    assert styles_view.border_left == ("rounded", Color.parse("green"))
    assert styles_view.border == (
        ("heavy", Color.parse("red")),
        ("", Color(0, 255, 0)),
        ("", Color(0, 255, 0)),
        ("rounded", Color.parse("green")),
    )


def test_get_opacity_default():
    styles = RenderStyles(DOMNode(), Styles(), Styles())
    assert styles.opacity == 1.0


@pytest.mark.parametrize(
    "set_value, expected",
    [
        [0.2, 0.2],
        [-0.4, 0.0],
        [5.8, 1.0],
        ["25%", 0.25],
        ["-10%", 0.0],
        ["120%", 1.0],
    ],
)
def test_opacity_set_then_get(set_value, expected):
    styles = RenderStyles(DOMNode(), Styles(), Styles())
    styles.opacity = set_value
    assert styles.opacity == expected


def test_opacity_set_invalid_type_error():
    styles = RenderStyles(DOMNode(), Styles(), Styles())
    with pytest.raises(StyleTypeError):
        styles.opacity = "invalid value"
