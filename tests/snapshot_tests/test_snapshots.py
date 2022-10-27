from pathlib import Path, PurePosixPath

import pytest

from textual.app import App
from textual.widgets import Input, Button


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
    press = [
        "tab",
        *"Darren",  # Focus first input, write "Darren"
        "tab",
        *"Burns",  # Tab focus to second input, write "Burns"
    ]
    assert snap_compare("docs/examples/widgets/input.py", press=press)

    # Assert that the state of the Input is what we'd expect
    # app: App = snap_compare.app
    # input: Input = app.query_one(Input)
    # assert input.value == "Darren"
    # assert input.cursor_position == 6
    # assert input.view_position == 0


def test_buttons_render(snap_compare):
    # Testing button rendering. We press tab to focus the first button too.
    assert snap_compare("docs/examples/widgets/button.py", press=["tab"])

    # app = snap_compare.app
    # button: Button = app.query_one(Button)
    # assert app.focused is button


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
    str(PurePosixPath(path))
    for path in Path("docs/examples/styles").iterdir()
    if path.suffix == ".py"
]


@pytest.mark.parametrize("path", PATHS)
def test_css_property_snapshot(path, snap_compare):
    assert snap_compare(path)
