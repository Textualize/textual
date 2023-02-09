import pytest

from textual.layouts.factory import MissingLayout, get_layout
from textual.layouts.vertical import VerticalLayout


def test_get_layout_valid_layout():
    layout = get_layout("vertical")
    assert type(layout) is VerticalLayout


def test_get_layout_invalid_layout():
    with pytest.raises(MissingLayout):
        get_layout("invalid")
