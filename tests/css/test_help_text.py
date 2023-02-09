import pytest

from tests.utilities.render import render
from textual.css._help_text import (
    align_help_text,
    border_property_help_text,
    color_property_help_text,
    fractional_property_help_text,
    layout_property_help_text,
    offset_property_help_text,
    offset_single_axis_help_text,
    scalar_help_text,
    spacing_invalid_value_help_text,
    spacing_wrong_number_of_values_help_text,
    string_enum_help_text,
    style_flags_property_help_text,
)


@pytest.fixture(params=["css", "inline"])
def styling_context(request):
    return request.param


def test_help_text_examples_are_contextualized():
    """Ensure that if the user is using CSS, they see CSS-specific examples
    and if they're using inline styles they see inline-specific examples."""
    rendered_inline = render(spacing_invalid_value_help_text("padding", "inline"))
    assert "widget.styles.padding" in rendered_inline

    rendered_css = render(spacing_invalid_value_help_text("padding", "css"))
    assert "padding:" in rendered_css


def test_spacing_wrong_number_of_values(styling_context):
    rendered = render(
        spacing_wrong_number_of_values_help_text("margin", 3, styling_context)
    )
    assert "Invalid number of values" in rendered
    assert "margin" in rendered
    assert "3" in rendered


def test_spacing_invalid_value(styling_context):
    rendered = render(spacing_invalid_value_help_text("padding", styling_context))
    assert "Invalid value for" in rendered
    assert "padding" in rendered


def test_scalar_help_text(styling_context):
    rendered = render(scalar_help_text("max-width", styling_context))
    assert "Invalid value for" in rendered

    # Ensure property name is contextualised to inline/css styling
    if styling_context == "css":
        assert "max-width" in rendered
    elif styling_context == "inline":
        assert "max_width" in rendered


def test_string_enum_help_text(styling_context):
    rendered = render(
        string_enum_help_text("display", ["none", "hidden"], styling_context)
    )
    assert "Invalid value for" in rendered

    # Ensure property name is mentioned
    assert "display" in rendered

    # Ensure each valid value is mentioned
    assert "hidden" in rendered
    assert "none" in rendered


def test_color_property_help_text(styling_context):
    rendered = render(color_property_help_text("background", styling_context))
    assert "Invalid value for" in rendered
    assert "background" in rendered


def test_border_property_help_text(styling_context):
    rendered = render(border_property_help_text("border", styling_context))
    assert "Invalid value for" in rendered
    assert "border" in rendered


def test_layout_property_help_text(styling_context):
    rendered = render(layout_property_help_text("layout", styling_context))
    assert "Invalid value for" in rendered
    assert "layout" in rendered


def test_fractional_property_help_text(styling_context):
    rendered = render(fractional_property_help_text("opacity", styling_context))
    assert "Invalid value for" in rendered
    assert "opacity" in rendered


def test_offset_property_help_text(styling_context):
    rendered = render(offset_property_help_text(styling_context))
    assert "Invalid value for" in rendered
    assert "offset" in rendered


def test_align_help_text():
    rendered = render(align_help_text())
    assert "Invalid value for" in rendered
    assert "align" in rendered


def test_offset_single_axis_help_text():
    rendered = render(offset_single_axis_help_text("offset-x"))
    assert "Invalid value for" in rendered
    assert "offset-x" in rendered


def test_style_flags_property_help_text(styling_context):
    rendered = render(
        style_flags_property_help_text("text-style", "notavalue b", styling_context)
    )
    assert "Invalid value" in rendered
    assert "notavalue" in rendered

    if styling_context == "css":
        assert "text-style" in rendered
    else:
        assert "text_style" in rendered
