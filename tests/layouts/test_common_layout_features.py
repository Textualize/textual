import pytest

from textual.screen import Screen
from textual.widget import Widget


@pytest.mark.parametrize(
    "layout,display,expected_in_displayed_children",
    [
        ("horizontal", "block", True),
        ("vertical", "block", True),
        ("horizontal", "none", False),
        ("vertical", "none", False),
    ],
)
def test_nodes_take_display_property_into_account_when_they_display_their_children(
    layout: str, display: str, expected_in_displayed_children: bool
):
    widget = Widget(name="widget that might not be visible 🥷 ")
    widget.styles.display = display

    screen = Screen()
    screen.styles.layout = layout
    screen._add_child(widget)

    displayed_children = screen.displayed_children
    assert isinstance(displayed_children, list)
    assert (widget in screen.displayed_children) is expected_in_displayed_children
