import pytest

from textual.layouts.dock import DockLayout
from textual.layouts.grid import GridLayout
from textual.layouts.vertical import VerticalLayout
from textual.view import View


@pytest.mark.parametrize("layout_name, layout_type", [
    ["dock", DockLayout],
    ["grid", GridLayout],
    ["vertical", VerticalLayout],
])
def test_view_layout_get_and_set(layout_name, layout_type):
    view = View()
    view.layout = layout_name
    assert type(view.layout) is layout_type
    assert view.styles.layout is view.layout
