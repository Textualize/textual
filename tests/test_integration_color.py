import pytest

from tests.utilities.test_app import AppTest
from textual.app import ComposeResult
from textual.color import Color, BLACK, WHITE
from textual.geometry import Size
from textual.widget import Widget


@pytest.mark.parametrize(
    "widget_color,widget_background_color,expected_color",
    (
        # "auto" on a white background --> foreground is black
        ["auto", "white", BLACK],
        # "auto" on a black background --> foreground is white
        ["auto", "black", WHITE],
        # And now with a pinch of alpha:
        ["auto 50%", "white", WHITE.get_contrast_text(0.5)],
        ["30% auto", "black", BLACK.get_contrast_text(0.3)],
    ),
)
def test_color_auto_single_widget(
    widget_color: str,
    widget_background_color: str,
    expected_color: Color,
):
    widget = Widget()
    widget.styles.color = widget_color
    widget.styles.background = widget_background_color

    (_, _), (_, color) = widget.colors
    assert color == expected_color


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "widget_color,widget_background_color,parent_background_color,expected_color,approx",
    (
        ##############
        # Simple cases first, with just the widget adapting is foreground color to its own background:
        ##############
        # "auto" on a white background --> foreground is black
        ["auto", "white", "transparent", BLACK, False],
        # "auto" on a black background --> foreground is white
        ["auto", "black", "transparent", WHITE, False],
        # "auto 40%" on a white background --> foreground is grey, somewhere between black and white
        ["auto 40%", "white", "transparent", WHITE.get_contrast_text(0.4), False],
        # "80% auto" on a black background --> foreground is grey, somewhere between black and white
        ["80% auto", "black", "transparent", BLACK.get_contrast_text(0.8), False],
        ##############
        # If the widget is transparent we should take into account the color of its ancestors:
        ##############
        ["auto", "transparent", "white", BLACK, False],
        ["auto", "transparent", "black", WHITE, False],
        ["auto 60%", "transparent", "white", WHITE.get_contrast_text(0.6), False],
        ["20% auto", "transparent", "black", BLACK.get_contrast_text(0.2), False],
        ##############
        # Now let's play a bit with opacity levels:
        ##############
        [
            "auto",
            "rgba(255, 0, 0, 0.5)",
            "white",
            (WHITE + Color(255, 0, 0, 0.5)).get_contrast_text(1),
            False,
        ],
        [
            # *Three* layers of opacity? Sure, let's do this:
            "auto 30%",
            "rgba(255, 0, 0, 0.2)",
            "rgba(0, 255, 0, 0.8)",
            (WHITE + Color(0, 255, 0, 0.8) + Color(255, 0, 0, 0.2)).get_contrast_text(
                0.3
            ),
            True,  # with these 3 layers we get approximation errors
        ],
    ),
)
async def test_color_auto(
    widget_color: str,
    widget_background_color: str,
    parent_background_color: str,
    expected_color: Color,
    approx: bool,  # let's use approximate equality tests only when we have to
):
    class WidgetWithText(Widget):
        def on_mount(self):
            self.styles.background = widget_background_color
            self.styles.color = widget_color

    class ParentWidget(Widget):
        def on_mount(self):
            self.styles.background = parent_background_color

    widget_with_text = WidgetWithText()
    parent_widget = ParentWidget(widget_with_text)

    class MyTestApp(AppTest):
        def compose(self) -> ComposeResult:
            yield parent_widget

    app = MyTestApp(size=Size(10, 1), test_name="test_color_auto")

    await app.boot_and_shutdown()

    style_at_widget_location = app.screen.get_style_at(0, 0)
    color_at_widget_location = Color.from_rich_color(style_at_widget_location.color)
    if approx:
        assert color_at_widget_location.normalized == pytest.approx(
            expected_color.normalized, abs=0.01
        )
    else:
        assert color_at_widget_location == expected_color
