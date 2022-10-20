from pathlib import Path

import pytest


# --- Layout related stuff ---

def test_grid_layout_basic(snap_compare):
    assert snap_compare("docs/examples/guide/layout/grid_layout1.py")


def test_grid_layout_basic_overflow(snap_compare):
    assert snap_compare("docs/examples/guide/layout/grid_layout2.py")


def test_grid_layout_gutter(snap_compare):
    assert snap_compare("docs/examples/guide/layout/grid_layout7_gutter.py")


def test_layers(snap_compare):
    assert snap_compare("docs/examples/guide/layout/layers.py")


def test_horizontal_layout(snap_compare):
    assert snap_compare("docs/examples/guide/layout/horizontal_layout.py")


def test_vertical_layout(snap_compare):
    assert snap_compare("docs/examples/guide/layout/vertical_layout.py")


def test_dock_layout_sidebar(snap_compare):
    assert snap_compare("docs/examples/guide/layout/dock_layout2_sidebar.py")


# --- Interacting with widgets ---

def test_checkboxes(snap_compare):
    """Tests checkboxes but also acts a regression test for using
    width: auto in a Horizontal layout context."""
    assert snap_compare("docs/examples/widgets/checkbox.py")


def test_input_and_focus(snap_compare):
    first_field = ["tab"] + list("Darren")  # Focus first input, write "Darren"
    second_field = ["tab"] + list("Burns")  # Tab focus to second input, write "Burns"
    assert snap_compare("docs/examples/widgets/input.py", press=first_field + second_field)


def test_buttons_render(snap_compare):
    # Testing button rendering. We press tab to focus the first button too.
    assert snap_compare("docs/examples/widgets/button.py", press=["tab"])


# --- CSS properties ---
# We have a canonical example for each CSS property that is shown in their docs.
# If any of these change, something has likely broken, so snapshot each of them.

PATHS = [
    str(path) for path in Path("docs/examples/styles").iterdir() if path.suffix == ".py"
]


@pytest.mark.parametrize("path", PATHS)
def test_css_property_snapshot(path, snap_compare):
    assert snap_compare(path)
