import pytest

from textual.app import App
from textual.widget import Widget, WidgetError


async def test_widget_move_child() -> None:
    """Test moving a widget in a child list."""

    # Test calling move_child with no direction.
    async with App().run_test() as pilot:
        child = Widget(Widget())
        await pilot.app.mount(child)
        with pytest.raises(WidgetError):
            pilot.app.screen.move_child(child)

    # Test calling move_child with more than one direction.
    async with App().run_test() as pilot:
        child = Widget(Widget())
        await pilot.app.mount(child)
        with pytest.raises(WidgetError):
            pilot.app.screen.move_child(child, before=1, after=2)

    # Test attempting to move a child that isn't ours.
    async with App().run_test() as pilot:
        child = Widget(Widget())
        await pilot.app.mount(child)
        with pytest.raises(WidgetError):
            pilot.app.screen.move_child(Widget(), before=child)

    # Test attempting to move relative to a widget that isn't a child.
    async with App().run_test() as pilot:
        child = Widget(Widget())
        await pilot.app.mount(child)
        with pytest.raises(WidgetError):
            pilot.app.screen.move_child(child, before=Widget())

    # Make a background set of widgets.
    widgets = [Widget(id=f"widget-{n}") for n in range(10)]

    # Test attempting to move past the end of the child list.
    async with App().run_test() as pilot:
        container = Widget(*widgets)
        await pilot.app.mount(container)
        with pytest.raises(WidgetError):
            container.move_child(widgets[0], before=len(widgets) + 10)

    # Test attempting to move before the end of the child list.
    async with App().run_test() as pilot:
        container = Widget(*widgets)
        await pilot.app.mount(container)
        with pytest.raises(WidgetError):
            container.move_child(widgets[0], before=-(len(widgets) + 10))

    # Test the different permutations of moving one widget before another.
    perms = ((1, 0), (widgets[1], 0), (1, widgets[0]), (widgets[1], widgets[0]))
    for child, target in perms:
        async with App().run_test() as pilot:
            container = Widget(*widgets)
            await pilot.app.mount(container)
            container.move_child(child, before=target)
            assert container._nodes[0].id == "widget-1"
            assert container._nodes[1].id == "widget-0"
            assert container._nodes[2].id == "widget-2"

    # Test the different permutations of moving one widget after another.
    perms = ((0, 1), (widgets[0], 1), (0, widgets[1]), (widgets[0], widgets[1]))
    for child, target in perms:
        async with App().run_test() as pilot:
            container = Widget(*widgets)
            await pilot.app.mount(container)
            container.move_child(child, after=target)
            assert container._nodes[0].id == "widget-1"
            assert container._nodes[1].id == "widget-0"
            assert container._nodes[2].id == "widget-2"

    # Test moving after a child after the last child.
    async with App().run_test() as pilot:
        container = Widget(*widgets)
        await pilot.app.mount(container)
        container.move_child(widgets[0], after=widgets[-1])
        assert container._nodes[0].id == "widget-1"
        assert container._nodes[-1].id == "widget-0"

    # Test moving after a child after the last child's numeric position.
    async with App().run_test() as pilot:
        container = Widget(*widgets)
        await pilot.app.mount(container)
        container.move_child(widgets[0], after=widgets[9])
        assert container._nodes[0].id == "widget-1"
        assert container._nodes[-1].id == "widget-0"
