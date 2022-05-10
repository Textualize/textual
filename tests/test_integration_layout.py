from __future__ import annotations
import asyncio
from typing import cast, List

import pytest

from tests.utilities.test_app import AppTest
from textual.app import ComposeResult
from textual.geometry import Size
from textual.widget import Widget
from textual.widgets import Placeholder

# Let's allow ourselves some abbreviated names for those tests,
# in order to make the test cases a bit easier to read :-)
SCREEN_W = 100  # width of our Screens
SCREEN_H = 8  # height of our Screens
SCREEN_SIZE = Size(SCREEN_W, SCREEN_H)
PLACEHOLDERS_DEFAULT_H = 3  # the default height for our Placeholder widgets


@pytest.mark.asyncio
@pytest.mark.integration_test  # this is a slow test, we may want to skip them in some contexts
@pytest.mark.parametrize(
    (
        "screen_size",
        "placeholders_count",
        "root_container_style",
        "placeholders_style",
        "expected_root_widget_virtual_size",
        "expected_placeholders_size",
        "expected_placeholders_offset_x",
    ),
    (
        [
            SCREEN_SIZE,
            1,
            "border: ;",  # #root has no border
            "",  # no specific placeholder style
            # #root's virtual size=screen size
            (SCREEN_W, SCREEN_H),
            # placeholders width=same than screen :: height=default height
            (SCREEN_W, PLACEHOLDERS_DEFAULT_H),
            # placeholders should be at offset 0
            0,
        ],
        [
            # "none" borders still allocate a space for the (invisible) border
            SCREEN_SIZE,
            1,
            "border: none;",  # #root has an invisible border
            "",  # no specific placeholder style
            # #root's virtual size is smaller because of its borders
            (SCREEN_W - 2, SCREEN_H - 2),
            # placeholders width=same than screen, minus 2 borders :: height=default height minus 2 borders
            (SCREEN_W - 2, PLACEHOLDERS_DEFAULT_H),
            # placeholders should be at offset 1 because of #root's border
            1,
        ],
        [
            SCREEN_SIZE,
            1,
            "border: solid white;",  # #root has a visible border
            "",  # no specific placeholder style
            # #root's virtual size is smaller because of its borders
            (SCREEN_W - 2, SCREEN_H - 2),
            # placeholders width=same than screen, minus 2 borders :: height=default height minus 2 borders
            (SCREEN_W - 2, PLACEHOLDERS_DEFAULT_H),
            # placeholders should be at offset 1 because of #root's border
            1,
        ],
        [
            SCREEN_SIZE,
            4,
            "border: solid white;",  # #root has a visible border
            "",  # no specific placeholder style
            # #root's virtual height should be as high as its stacked content
            (SCREEN_W - 2 - 1, PLACEHOLDERS_DEFAULT_H * 4),
            # placeholders width=same than screen, minus 2 borders, minus scrollbar :: height=default height minus 2 borders
            (SCREEN_W - 2 - 1, PLACEHOLDERS_DEFAULT_H),
            # placeholders should be at offset 1 because of #root's border
            1,
        ],
        [
            SCREEN_SIZE,
            1,
            "border: solid white;",  # #root has a visible border
            "align: center top;",  # placeholders are centered horizontally
            # #root's virtual size=screen size
            (SCREEN_W, SCREEN_H),
            # placeholders width=same than screen, minus 2 borders :: height=default height
            (SCREEN_W - 2, PLACEHOLDERS_DEFAULT_H),
            # placeholders should be at offset 1 because of #root's border
            1,
        ],
        [
            SCREEN_SIZE,
            4,
            "border: solid white;",  # #root has a visible border
            "align: center top;",  # placeholders are centered horizontally
            # #root's virtual height should be as high as its stacked content
            (SCREEN_W - 2 - 1, PLACEHOLDERS_DEFAULT_H * 4),
            # placeholders width=same than screen, minus 2 borders, minus scrollbar :: height=default height
            (SCREEN_W - 2 - 1, PLACEHOLDERS_DEFAULT_H),
            # placeholders should be at offset 1 because of #root's border
            1,
        ],
    ),
)
async def test_composition_of_vertical_container_with_children(
    screen_size: Size,
    placeholders_count: int,
    root_container_style: str,
    placeholders_style: str,
    expected_placeholders_size: tuple[int, int],
    expected_root_widget_virtual_size: tuple[int, int],
    expected_placeholders_offset_x: int,
    event_loop: asyncio.AbstractEventLoop,
):
    class VerticalContainer(Widget):
        CSS = (
            """
        VerticalContainer {
            layout: vertical;
            overflow: hidden auto;
            ${root_container_style}
        }
        
        VerticalContainer Placeholder {
            height: ${placeholders_height};
            ${placeholders_style}
        }
        """.replace(
                "${root_container_style}", root_container_style
            )
            .replace("${placeholders_height}", str(PLACEHOLDERS_DEFAULT_H))
            .replace("${placeholders_style}", placeholders_style)
        )

    class MyTestApp(AppTest):
        def compose(self) -> ComposeResult:
            placeholders = [
                Placeholder(id=f"placeholder_{i}", name=f"Placeholder #{i}")
                for i in range(placeholders_count)
            ]

            yield VerticalContainer(*placeholders, id="root")

    app = MyTestApp(size=screen_size, test_name="compositor")

    expected_screen_size = Size(*screen_size)

    async with app.in_running_state():
        app.log_tree()

        # root widget checks:
        root_widget = cast(Widget, app.get_child("root"))
        assert root_widget.size == expected_screen_size
        root_widget_region = app.screen.get_widget_region(root_widget)
        assert root_widget_region == (
            0,
            0,
            expected_screen_size.width,
            expected_screen_size.height,
        )

        app_placeholders = cast(List[Widget], app.query("Placeholder"))
        assert len(app_placeholders) == placeholders_count

    # placeholder widgets checks:
    for placeholder in app_placeholders:
        assert placeholder.size == expected_placeholders_size
        assert placeholder.styles.offset.x.value == 0.0
        assert app.screen.get_offset(placeholder).x == expected_placeholders_offset_x
