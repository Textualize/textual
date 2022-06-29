import pytest

from tests.utilities.test_app import AppTest
from textual.app import ComposeResult
from textual.color import Color, BLACK, WHITE
from textual.geometry import Size
from textual.widget import Widget


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "widget_color,widget_background_color,parent_background_color,expected_color,approx",
    (
        ["auto", "white", "transparent", BLACK, False],
        ["auto", "black", "transparent", WHITE, False],
        ["auto 50%", "white", "transparent", BLACK.get_contrast_text(0.5), False],
        ["auto 50%", "black", "transparent", WHITE.get_contrast_text(0.5), False],
        # If the widget is transparent we should take into account the color of its ancestors:
        ["auto", "transparent", "white", BLACK, False],
        ["auto", "transparent", "black", WHITE, False],
        ["auto 50%", "transparent", "white", BLACK.get_contrast_text(0.5), False],
        ["auto 50%", "transparent", "black", WHITE.get_contrast_text(0.5), False],
        # Now let's play a bit with opacity levels:
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
