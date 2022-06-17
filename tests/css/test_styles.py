import sys
from decimal import Decimal

if sys.version_info >= (3, 10):
    from typing import Literal
else:  # pragma: no cover
    from typing_extensions import Literal

import pytest

from rich.style import Style

from textual.app import ComposeResult
from textual.color import Color
from textual.css.errors import StyleValueError
from textual.css.scalar import Scalar, Unit
from textual.css.styles import Styles, RenderStyles
from textual.dom import DOMNode
from textual.widget import Widget

from tests.utilities.test_app import AppTest


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
    with pytest.raises(StyleValueError):
        styles.opacity = "invalid value"


@pytest.mark.parametrize(
    "size_dimension_input,size_dimension_expected_output",
    [
        # fmt: off
        [None, None],
        [1, Scalar(1, Unit.CELLS, Unit.WIDTH)],
        [1.0, Scalar(1.0, Unit.CELLS, Unit.WIDTH)],
        [1.2, Scalar(1.2, Unit.CELLS, Unit.WIDTH)],
        [1.2e3, Scalar(1200.0, Unit.CELLS, Unit.WIDTH)],
        ["20", Scalar(20, Unit.CELLS, Unit.WIDTH)],
        ["1.4", Scalar(1.4, Unit.CELLS, Unit.WIDTH)],
        [Scalar(100, Unit.CELLS, Unit.WIDTH), Scalar(100, Unit.CELLS, Unit.WIDTH)],
        [Scalar(10.3, Unit.CELLS, Unit.WIDTH), Scalar(10.3, Unit.CELLS, Unit.WIDTH)],
        [Scalar(10.4, Unit.CELLS, Unit.HEIGHT), Scalar(10.4, Unit.CELLS, Unit.HEIGHT)],
        [Scalar(10.5, Unit.PERCENT, Unit.WIDTH), Scalar(10.5, Unit.WIDTH, Unit.WIDTH)],
        [Scalar(10.6, Unit.PERCENT, Unit.PERCENT), Scalar(10.6, Unit.WIDTH, Unit.WIDTH)],
        [Scalar(10.7, Unit.HEIGHT, Unit.PERCENT), Scalar(10.7, Unit.HEIGHT, Unit.PERCENT)],
        # percentage values are normalised to floats and get the WIDTH "percent_unit":
        [Scalar(11, Unit.PERCENT, Unit.HEIGHT), Scalar(11.0, Unit.WIDTH, Unit.WIDTH)],
        # fmt: on
    ],
)
def test_widget_style_size_can_accept_various_data_types_and_normalize_them(
    size_dimension_input, size_dimension_expected_output
):
    widget = Widget()

    widget.styles.width = size_dimension_input
    assert widget.styles.width == size_dimension_expected_output


@pytest.mark.parametrize(
    "size_dimension_input",
    [
        "a",
        "1.4e3",
        3.14j,
        Decimal("3.14"),
        list(),
        tuple(),
        dict(),
    ],
)
def test_widget_style_size_fails_if_data_type_is_not_supported(size_dimension_input):
    widget = Widget()

    with pytest.raises(StyleValueError):
        widget.styles.width = size_dimension_input


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "overflow_y,scrollbar_gutter,scrollbar_size,text_length,expected_text_widget_width,expects_vertical_scrollbar",
    (
        # ------------------------------------------------
        # ----- Let's start with `overflow-y: auto`:
        # short text: full width, no scrollbar
        ["auto", "auto", 1, "short_text", 80, False],
        # long text: reduced width, scrollbar
        ["auto", "auto", 1, "long_text", 78, True],
        # short text, `scrollbar-gutter: stable`: reduced width, no scrollbar
        ["auto", "stable", 1, "short_text", 78, False],
        # long text, `scrollbar-gutter: stable`: reduced width, scrollbar
        ["auto", "stable", 1, "long_text", 78, True],
        # ------------------------------------------------
        # ----- And now let's see the behaviour with `overflow-y: scroll`:
        # short text: reduced width, scrollbar
        ["scroll", "auto", 1, "short_text", 78, True],
        # long text: reduced width, scrollbar
        ["scroll", "auto", 1, "long_text", 78, True],
        # short text, `scrollbar-gutter: stable`: reduced width, scrollbar
        ["scroll", "stable", 1, "short_text", 78, True],
        # long text, `scrollbar-gutter: stable`: reduced width, scrollbar
        ["scroll", "stable", 1, "long_text", 78, True],
        # ------------------------------------------------
        # ----- Finally, let's check the behaviour with `overflow-y: hidden`:
        # short text: full width, no scrollbar
        ["hidden", "auto", 1, "short_text", 80, False],
        # long text: full width, no scrollbar
        ["hidden", "auto", 1, "long_text", 80, False],
        # short text, `scrollbar-gutter: stable`: reduced width, no scrollbar
        ["hidden", "stable", 1, "short_text", 78, False],
        # long text, `scrollbar-gutter: stable`: reduced width, no scrollbar
        ["hidden", "stable", 1, "long_text", 78, False],
        # ------------------------------------------------
        # ----- Bonus round with a custom scrollbar size, now that we can set this:
        ["auto", "auto", 3, "short_text", 80, False],
        ["auto", "auto", 3, "long_text", 77, True],
        ["scroll", "auto", 3, "short_text", 77, True],
        ["scroll", "stable", 3, "short_text", 77, True],
        ["hidden", "auto", 3, "long_text", 80, False],
        ["hidden", "stable", 3, "short_text", 77, False],
    ),
)
async def test_scrollbar_gutter(
    overflow_y: str,
    scrollbar_gutter: str,
    scrollbar_size: int,
    text_length: Literal["short_text", "long_text"],
    expected_text_widget_width: int,
    expects_vertical_scrollbar: bool,
):
    from rich.text import Text
    from textual.geometry import Size

    class TextWidget(Widget):
        def render(self) -> Text:
            text_multiplier = 10 if text_length == "long_text" else 2
            return Text(
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit. In velit liber a a a."
                * text_multiplier
            )

    container = Widget()
    container.styles.height = 3
    container.styles.overflow_y = overflow_y
    container.styles.scrollbar_gutter = scrollbar_gutter
    if scrollbar_size > 1:
        container.styles.scrollbar_size_vertical = scrollbar_size

    text_widget = TextWidget()
    text_widget.styles.height = "auto"
    container.add_child(text_widget)

    class MyTestApp(AppTest):
        def compose(self) -> ComposeResult:
            yield container

    app = MyTestApp(test_name="scrollbar_gutter", size=Size(80, 10))
    await app.boot_and_shutdown()

    assert text_widget.size.width == expected_text_widget_width
    assert container.scrollbars_enabled[0] is expects_vertical_scrollbar
