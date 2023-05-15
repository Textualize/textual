from __future__ import annotations

import pytest

from textual.app import App
from textual.widget import Widget, WidgetError


async def test_move_child_no_direction() -> None:
    """Test moving a widget in a child list."""
    async with App().run_test() as pilot:
        child = Widget(Widget())
        await pilot.app.mount(child)
        with pytest.raises(WidgetError):
            pilot.app.screen.move_child(child)


async def test_move_child_both_directions() -> None:
    """Test calling move_child with more than one direction."""
    async with App().run_test() as pilot:
        child = Widget(Widget())
        await pilot.app.mount(child)
        with pytest.raises(WidgetError):
            pilot.app.screen.move_child(child, before=1, after=2)


async def test_move_child_not_our_child() -> None:
    """Test attempting to move a child that isn't ours."""
    async with App().run_test() as pilot:
        child = Widget(Widget())
        await pilot.app.mount(child)
        with pytest.raises(WidgetError):
            pilot.app.screen.move_child(Widget(), before=child)


async def test_move_child_to_outside() -> None:
    """Test attempting to move relative to a widget that isn't a child."""
    async with App().run_test() as pilot:
        child = Widget(Widget())
        await pilot.app.mount(child)
        with pytest.raises(WidgetError):
            pilot.app.screen.move_child(child, before=Widget())


async def test_move_child_before_itself() -> None:
    """Test moving a widget before itself."""

    async with App().run_test() as pilot:
        child = Widget(Widget())
        await pilot.app.mount(child)
        pilot.app.screen.move_child(child, before=child)


async def test_move_child_after_itself() -> None:
    """Test moving a widget after itself."""
    # Regression test for https://github.com/Textualize/textual/issues/1743
    async with App().run_test() as pilot:
        child = Widget(Widget())
        await pilot.app.mount(child)
        pilot.app.screen.move_child(child, after=child)


async def test_move_past_end_of_child_list() -> None:
    """Test attempting to move past the end of the child list."""
    async with App().run_test() as pilot:
        widgets = [Widget(id=f"widget-{n}") for n in range(10)]
        container = Widget(*widgets)
        await pilot.app.mount(container)
        with pytest.raises(WidgetError):
            container.move_child(widgets[0], before=len(widgets) + 10)


async def test_move_before_end_of_child_list() -> None:
    """Test attempting to move before the end of the child list."""
    async with App().run_test() as pilot:
        widgets = [Widget(id=f"widget-{n}") for n in range(10)]
        container = Widget(*widgets)
        await pilot.app.mount(container)
        with pytest.raises(WidgetError):
            container.move_child(widgets[0], before=-(len(widgets) + 10))


async def test_move_before_permutations() -> None:
    """Test the different permutations of moving one widget before another."""
    widgets = [Widget(id=f"widget-{n}") for n in range(10)]
    perms = ((1, 0), (widgets[1], 0), (1, widgets[0]), (widgets[1], widgets[0]))
    for child, target in perms:
        async with App().run_test() as pilot:
            container = Widget(*widgets)
            await pilot.app.mount(container)
            container.move_child(child, before=target)
            assert container._nodes[0].id == "widget-1"
            assert container._nodes[1].id == "widget-0"
            assert container._nodes[2].id == "widget-2"


async def test_move_after_permutations() -> None:
    """Test the different permutations of moving one widget after another."""
    widgets = [Widget(id=f"widget-{n}") for n in range(10)]
    perms = ((0, 1), (widgets[0], 1), (0, widgets[1]), (widgets[0], widgets[1]))
    for child, target in perms:
        async with App().run_test() as pilot:
            container = Widget(*widgets)
            await pilot.app.mount(container)
            container.move_child(child, after=target)
            assert container._nodes[0].id == "widget-1"
            assert container._nodes[1].id == "widget-0"
            assert container._nodes[2].id == "widget-2"


async def test_move_child_after_last_child() -> None:
    """Test moving after a child after the last child."""
    async with App().run_test() as pilot:
        widgets = [Widget(id=f"widget-{n}") for n in range(10)]
        container = Widget(*widgets)
        await pilot.app.mount(container)
        container.move_child(widgets[0], after=widgets[-1])
        assert container._nodes[0].id == "widget-1"
        assert container._nodes[-1].id == "widget-0"


async def test_move_child_after_last_numeric_location() -> None:
    """Test moving after a child after the last child's numeric position."""
    async with App().run_test() as pilot:
        widgets = [Widget(id=f"widget-{n}") for n in range(10)]
        container = Widget(*widgets)
        await pilot.app.mount(container)
        container.move_child(widgets[0], after=widgets[9])
        assert container._nodes[0].id == "widget-1"
        assert container._nodes[-1].id == "widget-0"
