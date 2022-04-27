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
