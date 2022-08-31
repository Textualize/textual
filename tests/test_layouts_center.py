from textual._layout import WidgetPlacement
from textual.geometry import Region, Size, Spacing
from textual.layouts.center import CenterLayout
from textual.widget import Widget


def test_center_layout():

    widget = Widget()
    widget._size = Size(80, 24)
    child = Widget()
    child.styles.width = 10
    child.styles.height = 5
    layout = CenterLayout()

    placements, widgets = layout.arrange(widget, [child], Size(60, 20))
    assert widgets == {child}

    expected = [
        WidgetPlacement(
            region=Region(x=25, y=7, width=10, height=5),
            margin=Spacing(),
            widget=child,
            order=0,
            fixed=False,
        ),
    ]
    assert placements == expected
