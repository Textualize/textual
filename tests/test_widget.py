import pytest

from textual.app import App
from textual.css.errors import StyleValueError
from textual.geometry import Size
from textual.widget import Widget


@pytest.mark.parametrize(
    "set_val, get_val, style_str",
    [
        [True, True, "visible"],
        [False, False, "hidden"],
        ["hidden", False, "hidden"],
        ["visible", True, "visible"],
    ],
)
def test_widget_set_visible_true(set_val, get_val, style_str):
    widget = Widget()
    widget.visible = set_val

    assert widget.visible is get_val
    assert widget.styles.visibility == style_str


def test_widget_set_visible_invalid_string():
    widget = Widget()

    with pytest.raises(StyleValueError):
        widget.visible = "nope! no widget for me!"

    assert widget.visible


def test_widget_content_width():
    class TextWidget(Widget):
        def __init__(self, text: str, id: str) -> None:
            self.text = text
            super().__init__(id=id)
            self.expand = False
            self.shrink = True

        def render(self) -> str:
            return self.text

    widget1 = TextWidget("foo", id="widget1")
    widget2 = TextWidget("foo\nbar", id="widget2")
    widget3 = TextWidget("foo\nbar\nbaz", id="widget3")

    app = App()
    app._set_active()

    width = widget1.get_content_width(Size(20, 20), Size(80, 24))
    height = widget1.get_content_height(Size(20, 20), Size(80, 24), width)
    assert width == 3
    assert height == 1

    width = widget2.get_content_width(Size(20, 20), Size(80, 24))
    height = widget2.get_content_height(Size(20, 20), Size(80, 24), width)
    assert width == 3
    assert height == 2

    width = widget3.get_content_width(Size(20, 20), Size(80, 24))
    height = widget3.get_content_height(Size(20, 20), Size(80, 24), width)
    assert width == 3
    assert height == 3
