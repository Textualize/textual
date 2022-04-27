from contextlib import nullcontext as does_not_raise
from decimal import Decimal

import pytest

from textual.css.errors import StyleValueError
from textual.css.scalar import Scalar, Unit
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


@pytest.mark.parametrize(
    "size_input, expectation",
    [
        (None, does_not_raise()),
        (10, does_not_raise()),
        (10.0, does_not_raise()),
        (10.2, does_not_raise()),
        (Scalar(100, Unit.CELLS, Unit.WIDTH), does_not_raise()),
        (Scalar(10.2, Unit.CELLS, Unit.WIDTH), does_not_raise()),
        ("10", does_not_raise()),
        # And now for some common types we don't handle...
        ("a", pytest.raises(StyleValueError)),
        (list(), pytest.raises(StyleValueError)),
        (tuple(), pytest.raises(StyleValueError)),
        (dict(), pytest.raises(StyleValueError)),
        (3.14j, pytest.raises(StyleValueError)),
        (Decimal("3.14"), pytest.raises(StyleValueError)),
    ],
)
def test_widget_style_size_can_accept_various_data_types(size_input, expectation):
    widget = Widget()

    with expectation:
        widget.styles.width = size_input
