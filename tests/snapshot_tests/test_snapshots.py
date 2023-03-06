from pathlib import Path

import pytest

from textual.widgets import Placeholder

# These paths should be relative to THIS directory.
WIDGET_EXAMPLES_DIR = Path("../../docs/examples/widgets")
LAYOUT_EXAMPLES_DIR = Path("../../docs/examples/guide/layout")
STYLES_EXAMPLES_DIR = Path("../../docs/examples/styles")
SNAPSHOT_APPS_DIR = Path("./snapshot_apps")


# --- Layout related stuff ---


def test_grid_layout_basic(snap_compare):
    assert snap_compare(LAYOUT_EXAMPLES_DIR / "grid_layout1.py")


def test_grid_layout_basic_overflow(snap_compare):
    assert snap_compare(LAYOUT_EXAMPLES_DIR / "grid_layout2.py")


def test_grid_layout_gutter(snap_compare):
    assert snap_compare(LAYOUT_EXAMPLES_DIR / "grid_layout7_gutter.py")


def test_layers(snap_compare):
    assert snap_compare(LAYOUT_EXAMPLES_DIR / "layers.py")


def test_horizontal_layout(snap_compare):
    assert snap_compare(LAYOUT_EXAMPLES_DIR / "horizontal_layout.py")


def test_horizontal_layout_width_auto_dock(snap_compare):
    assert snap_compare(SNAPSHOT_APPS_DIR / "horizontal_auto_width.py")


def test_vertical_layout(snap_compare):
    assert snap_compare(LAYOUT_EXAMPLES_DIR / "vertical_layout.py")


def test_dock_layout_sidebar(snap_compare):
    assert snap_compare(LAYOUT_EXAMPLES_DIR / "dock_layout2_sidebar.py")


# --- Widgets - rendering and basic interactions ---
# Each widget should have a canonical example that is display in the docs.
# When adding a new widget, ideally we should also create a snapshot test
# from these examples which test rendering and simple interactions with it.


def test_switches(snap_compare):
    """Tests switches but also acts a regression test for using
    width: auto in a Horizontal layout context."""
    press = [
        "shift+tab",
        "enter",  # toggle off
        "shift+tab",
        "wait:20",
        "enter",  # toggle on
        "wait:20",
    ]
    assert snap_compare(WIDGET_EXAMPLES_DIR / "switch.py", press=press)


def test_input_and_focus(snap_compare):
    press = [
        "tab",
        *"Darren",  # Focus first input, write "Darren"
        "tab",
        *"Burns",
        "_",  # Tab focus to second input, write "Burns"
    ]
    assert snap_compare(WIDGET_EXAMPLES_DIR / "input.py", press=press)


def test_buttons_render(snap_compare):
    # Testing button rendering. We press tab to focus the first button too.
    assert snap_compare(WIDGET_EXAMPLES_DIR / "button.py", press=["tab"])


def test_placeholder_render(snap_compare):
    # Testing the rendering of the multiple placeholder variants and labels.
    Placeholder.reset_color_cycle()
    assert snap_compare(WIDGET_EXAMPLES_DIR / "placeholder.py")


def test_datatable_render(snap_compare):
    press = ["tab", "down", "down", "right", "up", "left", "_"]
    assert snap_compare(WIDGET_EXAMPLES_DIR / "data_table.py", press=press)


def test_datatable_row_cursor_render(snap_compare):
    press = ["up", "left", "right", "down", "down", "_"]
    assert snap_compare(SNAPSHOT_APPS_DIR / "data_table_row_cursor.py", press=press)


def test_datatable_column_cursor_render(snap_compare):
    press = ["left", "up", "down", "right", "right", "_"]
    assert snap_compare(SNAPSHOT_APPS_DIR / "data_table_column_cursor.py", press=press)


def test_datatable_sort_multikey(snap_compare):
    press = ["down", "right", "s"]  # Also checks that sort doesn't move cursor.
    assert snap_compare(SNAPSHOT_APPS_DIR / "data_table_sort.py", press=press)


def test_datatable_labels_and_fixed_data(snap_compare):
    # Ensure that we render correctly when there are fixed rows/cols and labels.
    assert snap_compare(SNAPSHOT_APPS_DIR / "data_table_row_labels.py")


def test_footer_render(snap_compare):
    assert snap_compare(WIDGET_EXAMPLES_DIR / "footer.py")


def test_header_render(snap_compare):
    assert snap_compare(WIDGET_EXAMPLES_DIR / "header.py")


def test_list_view(snap_compare):
    assert snap_compare(
        WIDGET_EXAMPLES_DIR / "list_view.py", press=["tab", "down", "down", "up", "_"]
    )


def test_textlog_max_lines(snap_compare):
    assert snap_compare("snapshot_apps/textlog_max_lines.py", press=[*"abcde", "_"])


def test_fr_units(snap_compare):
    assert snap_compare("snapshot_apps/fr_units.py")


def test_visibility(snap_compare):
    assert snap_compare("snapshot_apps/visibility.py")


def test_tree_example(snap_compare):
    assert snap_compare(WIDGET_EXAMPLES_DIR / "tree.py")


def test_markdown_example(snap_compare):
    assert snap_compare(WIDGET_EXAMPLES_DIR / "markdown.py")


def test_markdown_viewer_example(snap_compare):
    assert snap_compare(WIDGET_EXAMPLES_DIR / "markdown_viewer.py")


def test_checkbox_example(snap_compare):
    assert snap_compare(WIDGET_EXAMPLES_DIR / "checkbox.py")


def test_radio_button_example(snap_compare):
    assert snap_compare(WIDGET_EXAMPLES_DIR / "radio_button.py")


def test_radio_set_example(snap_compare):
    assert snap_compare(WIDGET_EXAMPLES_DIR / "radio_set.py")


# --- CSS properties ---
# We have a canonical example for each CSS property that is shown in their docs.
# If any of these change, something has likely broken, so snapshot each of them.

PATHS = [
    path.name
    for path in (Path(__file__).parent / STYLES_EXAMPLES_DIR).iterdir()
    if path.suffix == ".py"
]


@pytest.mark.parametrize("file_name", PATHS)
def test_css_property(file_name, snap_compare):
    path_to_app = STYLES_EXAMPLES_DIR / file_name
    Placeholder.reset_color_cycle()
    assert snap_compare(path_to_app)


def test_multiple_css(snap_compare):
    # Interaction between multiple CSS files and app-level/classvar CSS
    assert snap_compare("snapshot_apps/multiple_css/multiple_css.py")


def test_order_independence(snap_compare):
    assert snap_compare("snapshot_apps/layer_order_independence.py")


def test_order_independence_toggle(snap_compare):
    assert snap_compare("snapshot_apps/layer_order_independence.py", press="t,_")


def test_columns_height(snap_compare):
    # Interaction with height auto, and relative heights to make columns
    assert snap_compare("snapshot_apps/columns_height.py")


def test_offsets(snap_compare):
    """Test offsets of containers"""
    assert snap_compare("snapshot_apps/offsets.py")


def test_nested_auto_heights(snap_compare):
    """Test refreshing widget within a auto sized container"""
    assert snap_compare("snapshot_apps/nested_auto_heights.py", press=["1", "2", "_"])


def test_programmatic_scrollbar_gutter_change(snap_compare):
    """Regression test for #1607 https://github.com/Textualize/textual/issues/1607

    See also tests/css/test_programmatic_style_changes.py for other related regression tests.
    """
    assert snap_compare(
        "snapshot_apps/programmatic_scrollbar_gutter_change.py", press=["s"]
    )


# --- Other ---


def test_key_display(snap_compare):
    assert snap_compare(SNAPSHOT_APPS_DIR / "key_display.py")


def test_demo(snap_compare):
    """Test the demo app (python -m textual)"""
    assert snap_compare(
        Path("../../src/textual/demo.py"),
        press=["down", "down", "down"],
        terminal_size=(100, 30),
    )


def test_label_widths(snap_compare):
    """Test renderable widths are calculate correctly."""
    assert snap_compare(SNAPSHOT_APPS_DIR / "label_widths.py")


def test_auto_width_input(snap_compare):
    assert snap_compare(
        SNAPSHOT_APPS_DIR / "auto_width_input.py", press=["tab", *"Hello"]
    )


def test_screen_switch(snap_compare):
    assert snap_compare(SNAPSHOT_APPS_DIR / "screen_switch.py", press=["a", "b"])


def test_disabled_widgets(snap_compare):
    assert snap_compare(SNAPSHOT_APPS_DIR / "disable_widgets.py")


def test_focus_component_class(snap_compare):
    assert snap_compare(SNAPSHOT_APPS_DIR / "focus_component_class.py", press=["tab"])


def test_line_api_scrollbars(snap_compare):
    assert snap_compare(SNAPSHOT_APPS_DIR / "line_api_scrollbars.py", press=["_"])
