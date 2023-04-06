from pathlib import Path

import pytest

from textual.widgets import Placeholder

# These paths should be relative to THIS directory.
WIDGET_EXAMPLES_DIR = Path("../../docs/examples/widgets")
LAYOUT_EXAMPLES_DIR = Path("../../docs/examples/guide/layout")
STYLES_EXAMPLES_DIR = Path("../../docs/examples/styles")
SNAPSHOT_APPS_DIR = Path("./snapshot_apps")
CLI_PREVIEWS_DIR = Path("../../src/textual/cli/previews")


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


def test_layout_containers(snap_compare):
    assert snap_compare(SNAPSHOT_APPS_DIR / "layout_containers.py")


def test_alignment_containers(snap_compare):
    assert snap_compare(SNAPSHOT_APPS_DIR / "alignment_containers.py")


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
        *"Burns",  # Focus second input, write "Burns"
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
    press = ["tab", "down", "down", "right", "up", "left"]
    assert snap_compare(WIDGET_EXAMPLES_DIR / "data_table.py", press=press)


def test_datatable_row_cursor_render(snap_compare):
    press = ["up", "left", "right", "down", "down"]
    assert snap_compare(SNAPSHOT_APPS_DIR / "data_table_row_cursor.py", press=press)


def test_datatable_column_cursor_render(snap_compare):
    press = ["left", "up", "down", "right", "right"]
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
        WIDGET_EXAMPLES_DIR / "list_view.py", press=["tab", "down", "down", "up"]
    )


def test_textlog_max_lines(snap_compare):
    assert snap_compare("snapshot_apps/textlog_max_lines.py", press=[*"abcde"])


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


def test_content_switcher_example_initial(snap_compare):
    assert snap_compare(WIDGET_EXAMPLES_DIR / "content_switcher.py")


def test_content_switcher_example_switch(snap_compare):
    assert snap_compare(
        WIDGET_EXAMPLES_DIR / "content_switcher.py",
        press=["tab", "tab", "enter", "wait:500"],
        terminal_size=(50, 50),
    )


def test_tabbed_content(snap_compare):
    assert snap_compare(WIDGET_EXAMPLES_DIR / "tabbed_content.py")


def test_option_list(snap_compare):
    assert snap_compare(WIDGET_EXAMPLES_DIR / "option_list_strings.py")
    assert snap_compare(WIDGET_EXAMPLES_DIR / "option_list_options.py")
    assert snap_compare(WIDGET_EXAMPLES_DIR / "option_list_tables.py")


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
    assert snap_compare("snapshot_apps/layer_order_independence.py", press="t")


def test_columns_height(snap_compare):
    # Interaction with height auto, and relative heights to make columns
    assert snap_compare("snapshot_apps/columns_height.py")


def test_offsets(snap_compare):
    """Test offsets of containers"""
    assert snap_compare("snapshot_apps/offsets.py")


def test_nested_auto_heights(snap_compare):
    """Test refreshing widget within a auto sized container"""
    assert snap_compare("snapshot_apps/nested_auto_heights.py", press=["1", "2"])


def test_programmatic_scrollbar_gutter_change(snap_compare):
    """Regression test for #1607 https://github.com/Textualize/textual/issues/1607

    See also tests/css/test_programmatic_style_changes.py for other related regression tests.
    """
    assert snap_compare(
        "snapshot_apps/programmatic_scrollbar_gutter_change.py", press=["s"]
    )


# --- CLI Preview Apps ---
# For our CLI previews e.g. `textual easing`, `textual colors` etc, we have snapshots


def test_borders_preview(snap_compare):
    assert snap_compare(CLI_PREVIEWS_DIR / "borders.py", press=["tab", "enter"])


def test_colors_preview(snap_compare):
    assert snap_compare(CLI_PREVIEWS_DIR / "colors.py")


def test_easing_preview(snap_compare):
    assert snap_compare(CLI_PREVIEWS_DIR / "easing.py")


def test_keys_preview(snap_compare):
    assert snap_compare(CLI_PREVIEWS_DIR / "keys.py", press=["a", "b"])


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


def test_border_alpha(snap_compare):
    """Test setting a border alpha."""
    assert snap_compare(SNAPSHOT_APPS_DIR / "border_alpha.py")


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
    assert snap_compare(SNAPSHOT_APPS_DIR / "line_api_scrollbars.py")


def test_remove_with_auto_height(snap_compare):
    assert snap_compare(
        SNAPSHOT_APPS_DIR / "remove_auto.py", press=["a", "a", "a", "d", "d"]
    )


def test_auto_table(snap_compare):
    assert snap_compare(SNAPSHOT_APPS_DIR / "auto-table.py", terminal_size=(120, 40))


def test_table_markup(snap_compare):
    assert snap_compare(SNAPSHOT_APPS_DIR / "table_markup.py")


def test_textlog_scroll(snap_compare):
    assert snap_compare(SNAPSHOT_APPS_DIR / "textlog_scroll.py")


def test_tabs_invalidate(snap_compare):
    assert snap_compare(
        SNAPSHOT_APPS_DIR / "tabs_invalidate.py",
        press=["tab", "right"],
    )


def test_scrollbar_thumb_height(snap_compare):
    assert snap_compare(
        SNAPSHOT_APPS_DIR / "scrollbar_thumb_height.py",
    )


def test_css_hot_reloading(snap_compare):
    """Regression test for https://github.com/Textualize/textual/issues/2063."""

    async def run_before(pilot):
        css_file = pilot.app.CSS_PATH
        with open(css_file, "w") as f:
            f.write("/* This file is purposefully empty. */\n")  # Clear all the CSS.
        await pilot.app._on_css_change()

    assert snap_compare(
        SNAPSHOT_APPS_DIR / "hot_reloading_app.py", run_before=run_before
    )


def test_layer_fix(snap_compare):
    # Check https://github.com/Textualize/textual/issues/1358
    assert snap_compare(SNAPSHOT_APPS_DIR / "layer_fix.py", press=["d"])


def test_modal_dialog_bindings_input(snap_compare):
    # Check https://github.com/Textualize/textual/issues/2194
    assert snap_compare(
        SNAPSHOT_APPS_DIR / "modal_screen_bindings.py",
        press=["enter", "tab", "h", "!", "left", "i", "tab"],
    )


def test_modal_dialog_bindings(snap_compare):
    # Check https://github.com/Textualize/textual/issues/2194
    assert snap_compare(
        SNAPSHOT_APPS_DIR / "modal_screen_bindings.py",
        press=["enter", "tab", "h", "i", "tab", "enter"],
    )


def test_dock_scroll(snap_compare):
    # https://github.com/Textualize/textual/issues/2188
    assert snap_compare(SNAPSHOT_APPS_DIR / "dock_scroll.py", terminal_size=(80, 25))


def test_auto_fr(snap_compare):
    # https://github.com/Textualize/textual/issues/2220
    assert snap_compare(SNAPSHOT_APPS_DIR / "auto_fr.py", terminal_size=(80, 25))


def test_fr_margins(snap_compare):
    # https://github.com/Textualize/textual/issues/2220
    assert snap_compare(SNAPSHOT_APPS_DIR / "fr_margins.py", terminal_size=(80, 25))


def test_scroll_visible(snap_compare):
    # https://github.com/Textualize/textual/issues/2181
    assert snap_compare(SNAPSHOT_APPS_DIR / "scroll_visible.py", press=["t"])
