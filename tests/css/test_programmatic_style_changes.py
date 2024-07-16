import pytest

from textual.app import App
from textual.containers import Grid
from textual.widgets import Label


@pytest.mark.parametrize(
    "style, value",
    [
        ("grid_size_rows", 3),
        ("grid_size_columns", 3),
        ("grid_gutter_vertical", 4),
        ("grid_gutter_horizontal", 4),
        ("grid_rows", "1fr 3fr"),
        ("grid_columns", "1fr 3fr"),
    ],
)
async def test_programmatic_style_change_updates_children(style: str, value: object):
    """Regression test for #1607 https://github.com/Textualize/textual/issues/1607

    Some programmatic style changes to a widget were not updating the layout of the
    children widgets, which seemed to be happening when the style change did not affect
    the size of the widget but did affect the layout of the children.

    This test, in particular, checks the attributes that _should_ affect the size of the
    children widgets.
    """

    class MyApp(App[None]):
        CSS = """
        Grid { grid-size: 2 2; }
        Label { width: 100%; height: 100%; }
        """

        def compose(self):
            yield Grid(
                Label("one"),
                Label("two"),
                Label("three"),
                Label("four"),
            )

    app = MyApp()

    async with app.run_test() as pilot:
        sizes = [(lbl.size.width, lbl.size.height) for lbl in app.screen.query(Label)]

        setattr(app.query_one(Grid).styles, style, value)
        await pilot.pause()

        assert sizes != [
            (lbl.size.width, lbl.size.height) for lbl in app.screen.query(Label)
        ]


@pytest.mark.parametrize(
    "style, value",
    [
        ("align_horizontal", "right"),
        ("align_vertical", "bottom"),
        ("align", ("right", "bottom")),
    ],
)
async def test_programmatic_align_change_updates_children_position(
    style: str, value: str
):
    """Regression test for #1607 for the align(_xxx) styles.

    See https://github.com/Textualize/textual/issues/1607.
    """

    class MyApp(App[None]):
        CSS = "Grid { grid-size: 2 2; }"

        def compose(self):
            yield Grid(
                Label("one"),
                Label("two"),
                Label("three"),
                Label("four"),
            )

    app = MyApp()

    async with app.run_test() as pilot:
        offsets = [(lbl.region.x, lbl.region.y) for lbl in app.screen.query(Label)]

        setattr(app.query_one(Grid).styles, style, value)
        await pilot.pause()

        assert offsets != [
            (lbl.region.x, lbl.region.y) for lbl in app.screen.query(Label)
        ]
