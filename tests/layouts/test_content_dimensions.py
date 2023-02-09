import pytest

from textual.geometry import Size
from textual.layouts.grid import GridLayout
from textual.layouts.horizontal import HorizontalLayout
from textual.layouts.vertical import VerticalLayout
from textual.widget import Widget

LAYOUTS = [GridLayout, HorizontalLayout, VerticalLayout]


@pytest.mark.parametrize("layout", LAYOUTS)
def test_empty_widget_height(layout):
    """Test that an empty widget has height equal to 0."""
    l = layout()
    # Make sure this measurement does not depend on the width.
    assert l.get_content_height(Widget(), Size(80, 24), Size(80, 24), 24) == 0
    assert l.get_content_height(Widget(), Size(80, 24), Size(80, 24), 20) == 0
    assert l.get_content_height(Widget(), Size(80, 24), Size(80, 24), 10) == 0
    assert l.get_content_height(Widget(), Size(80, 24), Size(80, 24), 0) == 0


@pytest.mark.parametrize("layout", LAYOUTS)
def test_empty_widget_width(layout):
    """Test that an empty widget has width equal to 0."""
    l = layout()
    assert l.get_content_width(Widget(), Size(80, 24), Size(80, 24)) == 0
