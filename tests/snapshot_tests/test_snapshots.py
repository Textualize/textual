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


# --- Widgets - rendering and basic interactions ---
# Each widget should have a canonical example that is display in the docs.
# When adding a new widget, ideally we should also create a snapshot test
# from these examples which test rendering and simple interactions with it.

# before snapshot test:
# src/textual/widgets/_checkbox.py              47     47     0%   1-126
# before testing presses in snapshot test:
# src/textual/widgets/_checkbox.py              47     11    77%   83-88, 110, 113, 118, 124-126
# after testing presses in snapshot test:
# src/textual/widgets/_checkbox.py              47      2    96%   87, 110

def test_checkboxes(snap_compare):
    """Tests checkboxes but also acts a regression test for using
    width: auto in a Horizontal layout context."""
    press = [
        "shift+tab",
        "enter",  # toggle off
        "shift+tab",
        "wait:20",
        "enter",  # toggle on
        "wait:20",
    ]
    assert snap_compare("docs/examples/widgets/checkbox.py", press=press)


def test_input_and_focus(snap_compare):
    first_field = ["tab"] + list("Darren")  # Focus first input, write "Darren"
    second_field = ["tab"] + list("Burns")  # Tab focus to second input, write "Burns"
    assert snap_compare("docs/examples/widgets/input.py", press=first_field + second_field)


def test_buttons_render(snap_compare):
    # Testing button rendering. We press tab to focus the first button too.
    assert snap_compare("docs/examples/widgets/button.py", press=["tab"])


# src/textual/widgets/_data_table.py           312    312     0%
# src/textual/widgets/_data_table.py           312     85    73%
def test_datatable_render(snap_compare):
    press = ["tab", "down", "down", "right", "up", "left"]
    assert snap_compare("docs/examples/widgets/data_table.py", press=press)


def test_footer_render(snap_compare):
    assert snap_compare("docs/examples/widgets/footer.py")


def test_header_render(snap_compare):
    assert snap_compare("docs/examples/widgets/header.py")

# --- CSS properties ---
# We have a canonical example for each CSS property that is shown in their docs.
# If any of these change, something has likely broken, so snapshot each of them.

PATHS = [
    str(path) for path in Path("docs/examples/styles").iterdir() if path.suffix == ".py"
]


@pytest.mark.parametrize("path", PATHS)
def test_css_property_snapshot(path, snap_compare):
    assert snap_compare(path)
