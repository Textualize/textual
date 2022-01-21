import pytest

from textual.layouts.dock import DockLayout
from textual.layouts.factory import get_layout, MissingLayout


def test_get_layout_valid_layout():
    layout_class = get_layout("dock")
    assert type(layout_class) is DockLayout


def test_get_layout_invalid_layout():
    with pytest.raises(MissingLayout):
        get_layout("invalid")
