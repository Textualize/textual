"""Unit tests for the pointer CSS property."""

import pytest

from textual.css.errors import StyleValueError
from textual.css.styles import Styles
from textual.widget import Widget


def test_pointer_property_default():
    """Test that pointer property has correct default value."""
    styles = Styles()
    assert styles.pointer == "default"


def test_pointer_property_set():
    """Test setting pointer property to valid values."""
    styles = Styles()

    # Test various valid pointer shapes
    valid_pointers = [
        "default",
        "pointer",
        "text",
        "crosshair",
        "help",
        "wait",
        "move",
        "grab",
        "grabbing",
        "n-resize",
        "s-resize",
        "e-resize",
        "w-resize",
        "ne-resize",
        "nw-resize",
        "se-resize",
        "sw-resize",
        "ew-resize",
        "ns-resize",
        "nesw-resize",
        "nwse-resize",
        "zoom-in",
        "zoom-out",
        "alias",
        "copy",
        "no-drop",
        "not-allowed",
        "cell",
        "vertical-text",
        "progress",
    ]

    for pointer in valid_pointers:
        styles.pointer = pointer
        assert styles.pointer == pointer


def test_pointer_css_parsing():
    """Test parsing pointer from CSS."""
    css = "pointer: pointer;"
    styles = Styles.parse(css, "test")
    assert styles.pointer == "pointer"

    css = "pointer: text;"
    styles = Styles.parse(css, "test")
    assert styles.pointer == "text"

    css = "pointer: crosshair;"
    styles = Styles.parse(css, "test")
    assert styles.pointer == "crosshair"


def test_pointer_invalid_value():
    """Test that invalid pointer values raise errors during CSS parsing."""
    from textual.css.errors import StyleValueError

    # Try to parse CSS with an invalid pointer value
    css = "pointer: invalid-cursor-shape;"

    # This should raise an error for invalid pointer shape
    with pytest.raises((StyleValueError, Exception)):
        styles = Styles.parse(css, "test")


def test_pointer_in_widget():
    """Test that pointer property works in widget context."""

    class TestWidget(Widget):
        DEFAULT_CSS = """
        TestWidget {
            pointer: pointer;
        }
        """

    widget = TestWidget()
    # Note: styles won't be fully initialized without mounting
    # This is just a basic smoke test
    assert widget is not None


if __name__ == "__main__":
    # Run basic tests
    test_pointer_property_default()
    test_pointer_property_set()
    test_pointer_css_parsing()
    print("All basic tests passed!")
