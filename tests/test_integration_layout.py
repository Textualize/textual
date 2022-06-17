from __future__ import annotations
from typing import cast, List, Sequence

import pytest
from rich.console import RenderableType
from rich.text import Text

from tests.utilities.test_app import AppTest
from textual.app import ComposeResult
from textual.css.types import EdgeType
from textual.geometry import Size
from textual.widget import Widget
from textual.widgets import Placeholder

# Let's allow ourselves some abbreviated names for those tests,
# in order to make the test cases a bit easier to read :-)
SCREEN_W = 100  # width of our Screens
SCREEN_H = 8  # height of our Screens
SCREEN_SIZE = Size(SCREEN_W, SCREEN_H)
PLACEHOLDERS_DEFAULT_H = 3  # the default height for our Placeholder widgets

# TODO: Brittle test
# These tests are currently way to brittle due to the CSS layout not being final
# They are also very hard to follow, if they break its not clear *what* went wrong
# Going to leave them marked as "skip" for now.


@pytest.mark.skip("brittle")
@pytest.mark.asyncio
@pytest.mark.integration_test  # this is a slow test, we may want to skip them in some contexts
@pytest.mark.parametrize(
    (
        "placeholders_count",
        "root_container_style",
        "placeholders_style",
        "expected_root_widget_virtual_size",
        "expected_placeholders_size",
        "expected_placeholders_offset_x",
    ),
    (
        *[
            [
                1,
                f"border: {invisible_border_edge};",  # #root has no visible border
                "",  # no specific placeholder style
                # #root's virtual size=screen size
                (SCREEN_W, SCREEN_H),
                # placeholders width=same than screen :: height=default height
                (SCREEN_W, PLACEHOLDERS_DEFAULT_H),
                # placeholders should be at offset 0
                0,
            ]
            for invisible_border_edge in ("", "none", "hidden")
        ],
        [
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
    placeholders_count: int,
    root_container_style: str,
    placeholders_style: str,
    expected_placeholders_size: tuple[int, int],
    expected_root_widget_virtual_size: tuple[int, int],
    expected_placeholders_offset_x: int,
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

    app = MyTestApp(size=SCREEN_SIZE, test_name="compositor")

    expected_screen_size = SCREEN_SIZE

    async with app.in_running_state():
        # root widget checks:
        root_widget = cast(Widget, app.get_child("root"))
        assert root_widget.size == expected_screen_size
        root_widget_region = app.screen.find_widget(root_widget).region
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


@pytest.mark.asyncio
@pytest.mark.integration_test
@pytest.mark.parametrize(
    "edge_type,expected_box_inner_size,expected_box_size,expected_top_left_edge_color,expects_visible_char_at_top_left_edge",
    (
        # These first 3 types of border edge types are synonyms, and display no borders:
        ["", Size(SCREEN_W, 1), Size(SCREEN_W, 1), "black", False],
        ["none", Size(SCREEN_W, 1), Size(SCREEN_W, 1), "black", False],
        ["hidden", Size(SCREEN_W, 1), Size(SCREEN_W, 1), "black", False],
        # Let's transition to "blank": we still see no visible border, but the size is increased
        # as the gutter space is reserved the same way it would be with a border:
        ["blank", Size(SCREEN_W - 2, 1), Size(SCREEN_W, 3), "#ffffff", False],
        # And now for the "normally visible" border edge types:
        # --> we see a visible border, and the size is increased:
        *[
            [edge_style, Size(SCREEN_W - 2, 1), Size(SCREEN_W, 3), "#ffffff", True]
            for edge_style in [
                "round",
                "solid",
                "double",
                "dashed",
                "heavy",
                "inner",
                "outer",
                "hkey",
                "vkey",
                "tall",
                "wide",
            ]
        ],
    ),
)
async def test_border_edge_types_impact_on_widget_size(
    edge_type: EdgeType,
    expected_box_inner_size: Size,
    expected_box_size: Size,
    expected_top_left_edge_color: str,
    expects_visible_char_at_top_left_edge: bool,
):
    class BorderTarget(Widget):
        def render(self) -> RenderableType:
            return Text("border target", style="black on yellow", justify="center")

    border_target = BorderTarget()
    border_target.styles.height = "auto"
    border_target.styles.border = (edge_type, "white")

    class MyTestApp(AppTest):
        def compose(self) -> ComposeResult:
            yield border_target

    app = MyTestApp(size=SCREEN_SIZE, test_name="border_edge_types")

    await app.boot_and_shutdown()

    box_inner_size = Size(
        border_target.content_region.width,
        border_target.content_region.height,
    )
    assert box_inner_size == expected_box_inner_size

    assert border_target.size == expected_box_size

    top_left_edge_style = app.screen.get_style_at(0, 0)
    top_left_edge_color = top_left_edge_style.color.name
    assert top_left_edge_color == expected_top_left_edge_color

    top_left_edge_char = app.get_char_at(0, 0)
    top_left_edge_char_is_a_visible_one = top_left_edge_char != " "
    assert top_left_edge_char_is_a_visible_one == expects_visible_char_at_top_left_edge


@pytest.mark.skip("brittle")
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "large_widget_size,container_style,expected_large_widget_visible_region_size",
    (
        # In these tests we're going to insert a "large widget"
        # into a container with size (20,20).
        # ---------------- let's start!
        # no overflow/scrollbar instructions: no scrollbars
        [Size(30, 30), "color: red", Size(20, 20)],
        # explicit hiding of the overflow: no scrollbars either
        [Size(30, 30), "overflow: hidden", Size(20, 20)],
        # scrollbar for both directions
        [Size(30, 30), "overflow: auto", Size(19, 19)],
        # horizontal scrollbar
        [Size(30, 30), "overflow-x: auto", Size(20, 19)],
        # vertical scrollbar
        [Size(30, 30), "overflow-y: auto", Size(19, 20)],
        # scrollbar for both directions, custom scrollbar size
        [Size(30, 30), ("overflow: auto", "scrollbar-size: 3 5"), Size(15, 17)],
        # scrollbar for both directions, custom vertical scrollbar size
        [Size(30, 30), ("overflow: auto", "scrollbar-size-vertical: 3"), Size(17, 19)],
        # scrollbar for both directions, custom horizontal scrollbar size
        [
            Size(30, 30),
            ("overflow: auto", "scrollbar-size-horizontal: 3"),
            Size(19, 17),
        ],
        # scrollbar needed only vertically, custom scrollbar size
        [
            Size(20, 30),
            ("overflow: auto", "scrollbar-size: 3 3"),
            Size(17, 20),
        ],
        # scrollbar needed only horizontally, custom scrollbar size
        [
            Size(30, 20),
            ("overflow: auto", "scrollbar-size: 3 3"),
            Size(20, 17),
        ],
    ),
)
async def test_scrollbar_size_impact_on_the_layout(
    large_widget_size: Size,
    container_style: str | Sequence[str],
    expected_large_widget_visible_region_size: Size,
):
    class LargeWidget(Widget):
        def on_mount(self):
            self.styles.width = large_widget_size[0]
            self.styles.height = large_widget_size[1]

    class LargeWidgetContainer(Widget):
        CSS = """
        LargeWidgetContainer {
            width: 20;
            height: 20;
            ${container_style};
        }
        """.replace(
            "${container_style}",
            container_style
            if isinstance(container_style, str)
            else ";".join(container_style),
        )

    large_widget = LargeWidget()
    container = LargeWidgetContainer(large_widget)

    class MyTestApp(AppTest):
        def compose(self) -> ComposeResult:
            yield container

    app = MyTestApp(size=Size(40, 40), test_name="scrollbar_size_impact_on_the_layout")

    await app.boot_and_shutdown()

    compositor = app.screen._compositor
    widgets_map = compositor.map
    large_widget_visible_region_size = widgets_map[large_widget].visible_region.size
    assert large_widget_visible_region_size == expected_large_widget_visible_region_size
