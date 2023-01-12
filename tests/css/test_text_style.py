from rich.style import Style

from textual.css.styles import Styles


def test_text_style_none():
    styles = Styles()
    styles.text_style = "none"
    assert styles.text_style == Style()


def test_text_style_none_with_others():
    """Style "none" mixed with others should result in empty style."""
    styles = Styles()
    styles.text_style = "bold none underline italic"

    none_styles = Styles()
    styles.text_style = "none"

    assert styles.text_style == none_styles.text_style
