import pytest

from textual._arrange import TOP_Z, arrange
from textual._layout import WidgetPlacement
from textual.app import App
from textual.geometry import Region, Size, Spacing
from textual.widget import Widget


def test_arrange_empty():
    container = Widget(id="container")

    result = arrange(container, [], Size(80, 24), Size(80, 24))
    assert result.placements == []
    assert result.widgets == set()


def test_arrange_dock_top():
    container = Widget(id="container")
    container._parent = App()
    child = Widget(id="child")
    header = Widget(id="header")
    header.styles.dock = "top"
    header.styles.height = "1"

    result = arrange(container, [child, header], Size(80, 24), Size(80, 24))

    assert result.placements == [
        WidgetPlacement(
            Region(0, 0, 80, 1), Spacing(), header, order=TOP_Z, fixed=True
        ),
        WidgetPlacement(Region(0, 1, 80, 23), Spacing(), child, order=0, fixed=False),
    ]
    assert result.widgets == {child, header}


def test_arrange_dock_left():
    container = Widget(id="container")
    container._parent = App()
    child = Widget(id="child")
    header = Widget(id="header")
    header.styles.dock = "left"
    header.styles.width = "10"

    result = arrange(container, [child, header], Size(80, 24), Size(80, 24))
    assert result.placements == [
        WidgetPlacement(
            Region(0, 0, 10, 24), Spacing(), header, order=TOP_Z, fixed=True
        ),
        WidgetPlacement(Region(10, 0, 70, 24), Spacing(), child, order=0, fixed=False),
    ]
    assert result.widgets == {child, header}


def test_arrange_dock_right():
    container = Widget(id="container")
    container._parent = App()
    child = Widget(id="child")
    header = Widget(id="header")
    header.styles.dock = "right"
    header.styles.width = "10"

    result = arrange(container, [child, header], Size(80, 24), Size(80, 24))
    assert result.placements == [
        WidgetPlacement(
            Region(70, 0, 10, 24), Spacing(), header, order=TOP_Z, fixed=True
        ),
        WidgetPlacement(Region(0, 0, 70, 24), Spacing(), child, order=0, fixed=False),
    ]
    assert result.widgets == {child, header}


def test_arrange_dock_bottom():
    container = Widget(id="container")
    container._parent = App()
    child = Widget(id="child")
    header = Widget(id="header")
    header.styles.dock = "bottom"
    header.styles.height = "1"

    result = arrange(container, [child, header], Size(80, 24), Size(80, 24))
    assert result.placements == [
        WidgetPlacement(
            Region(0, 23, 80, 1), Spacing(), header, order=TOP_Z, fixed=True
        ),
        WidgetPlacement(Region(0, 0, 80, 23), Spacing(), child, order=0, fixed=False),
    ]
    assert result.widgets == {child, header}


def test_arrange_dock_badly():
    child = Widget(id="child")
    child.styles.dock = "nowhere"
    with pytest.raises(AssertionError):
        _ = arrange(Widget(), [child], Size(80, 24), Size(80, 24))
