from rich.style import Style

from textual.css.styles import Styles


def test_styles_reset():
    styles = Styles()
    styles.text_style = "not bold"
    assert styles.text_style == Style(bold=False)
    styles.reset()
    assert styles.text_style is Style.null()
