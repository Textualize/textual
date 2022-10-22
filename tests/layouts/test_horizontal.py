from textual.geometry import Size
from textual.layouts.horizontal import HorizontalLayout
from textual.widget import Widget


class SizedWidget(Widget):
    """Simple Widget wrapped allowing you to modify the return values for
    get_content_width and get_content_height via the constructor."""

    def __init__(
        self,
        *children: Widget,
        content_width: int = 10,
        content_height: int = 5,
    ):
        super().__init__(*children)
        self.content_width = content_width
        self.content_height = content_height

    def get_content_width(self, container: Size, viewport: Size) -> int:
        return self.content_width

    def get_content_height(self, container: Size, viewport: Size, width: int) -> int:
        return self.content_height


CHILDREN = [
    SizedWidget(content_width=10, content_height=5),
    SizedWidget(content_width=4, content_height=2),
    SizedWidget(content_width=12, content_height=3),
]


def test_horizontal_get_content_width():
    parent = Widget(*CHILDREN)
    layout = HorizontalLayout()
    width = layout.get_content_width(widget=parent, container=Size(), viewport=Size())
    assert width == sum(child.content_width for child in CHILDREN)


def test_horizontal_get_content_width_no_children():
    parent = Widget()
    layout = HorizontalLayout()
    container_size = Size(24, 24)
    width = layout.get_content_width(widget=parent, container=container_size, viewport=Size())
    assert width == container_size.width
