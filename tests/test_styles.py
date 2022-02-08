from rich.color import Color
from rich.style import Style

from textual.css.styles import Styles, RenderStyles


def test_styles_reset():
    styles = Styles()
    styles.text_style = "not bold"
    assert styles.text_style == Style(bold=False)
    styles.reset()
    assert styles.text_style is Style.null()


def test_styles_view_text():
    """Test inline styles override base styles"""
    base = Styles()
    inline = Styles()
    styles_view = RenderStyles(None, base, inline)

    # Both styles are empty
    assert styles_view.text == Style()

    # Base is bold blue
    base.text_color = "blue"
    base.text_style = "bold"
    assert styles_view.text == Style.parse("bold blue")

    # Base is bold blue, inline is red
    inline.text_color = "red"
    assert styles_view.text == Style.parse("bold red")

    # Base is bold yellow, inline is red
    base.text_color = "yellow"
    assert styles_view.text == Style.parse("bold red")

    # Base is bold blue
    inline.text_color = None
    assert styles_view.text == Style.parse("bold yellow")


def test_styles_view_border():

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
        ("", Color.default()),
        ("", Color.default()),
        ("rounded", Color.parse("green")),
    )
