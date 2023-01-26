import pytest

from textual.app import App
from textual.containers import Grid
from textual.screen import Screen
from textual.widgets import Label


updates = 0


class _Label(Label):
    """Label widget that keeps track of its own updates."""

    def refresh(self, *args, **kwargs):
        global updates
        updates += 1
        return super().refresh(*args, **kwargs)


@pytest.mark.parametrize(
    "style, value",
    [
        ("grid_size_rows", 2),
        ("grid_size_columns", 2),
        ("grid_gutter_vertical", 2),
        ("grid_gutter_horizontal", 1),
        ("grid_rows", "1fr 3fr"),
        ("grid_columns", "1fr 3fr"),
        ("scrollbar_gutter", "stable"),
        ("align_horizontal", "right"),
        ("align_vertical", "bottom"),
        ("align", ("right", "bottom")),
    ],
)
def test_programmatic_style_change_refreshes_children_layout(style: str, value):
    """Regression test for #1607 https://github.com/Textualize/textual/issues/1607

    Some programmatic style changes to a widget were not updating the layout of the
    children widgets, which seemed to be happening when the style change did not affect
    the size of the widget but did affect the layout of the children.
    """

    global updates

    app = App()
    app.DEFAULT_CSS = "Grid { grid-size: 1 1; }"
    app._set_active()
    app.push_screen(Screen())

    grid = Grid(
        _Label("one"),
        _Label("two"),
        _Label("three"),
        _Label("four"),
    )
    app.screen._add_children(grid)

    update_count = updates
    setattr(grid.styles, style, value)
    print(updates, update_count)
    assert updates > update_count
