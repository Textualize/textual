import pytest

from textual.widgets import Placeholder
from textual.widgets._placeholder import InvalidPlaceholderVariant


def test_invalid_placeholder_variant():
    with pytest.raises(InvalidPlaceholderVariant):
        Placeholder(variant="this is clearly not a valid variant!")


def test_invalid_reactive_variant_change():
    p = Placeholder()
    with pytest.raises(InvalidPlaceholderVariant):
        p.variant = "this is clearly not a valid variant!"
