import pytest

from textual.app import App
from textual.css.query import TooManyMatches
from textual.widget import MountError, Widget, WidgetError
from textual.widgets import Static


class SelfOwn(Widget):
    """Test a widget that tries to own itself."""

    def __init__(self) -> None:
        super().__init__(self)


async def test_mount_via_app() -> None:
    """Perform mount tests via the app."""

    # Make a background set of widgets.
    widgets = [Static(id=f"starter-{n}") for n in range(10)]

    async with App[None]().run_test() as pilot:
        with pytest.raises(WidgetError):
            await pilot.app.mount(SelfOwn())

    async with App().run_test() as pilot:
        # Mount the first one and make sure it's there.
        await pilot.app.mount(widgets[0])
        assert len(pilot.app.screen._nodes) == 1
        assert pilot.app.screen._nodes[0] == widgets[0]

        # Mount the next 2 widgets via mount.
        await pilot.app.mount(*widgets[1:3])
        assert list(pilot.app.screen._nodes) == widgets[0:3]

        # Finally mount the rest of the widgets via mount_all.
        await pilot.app.mount_all(widgets[3:])
        assert list(pilot.app.screen._nodes) == widgets

    async with App().run_test() as pilot:
        # Mount a widget before -1, which is "before the end".
        penultimate = Static(id="penultimate")
        await pilot.app.mount_all(widgets)
        await pilot.app.mount(penultimate, before=-1)
        assert pilot.app.screen._nodes[-2] == penultimate

    async with App().run_test() as pilot:
        # Mount a widget after -1, which is "at the end".
        ultimate = Static(id="ultimate")
        await pilot.app.mount_all(widgets)
        await pilot.app.mount(ultimate, after=-1)
        assert pilot.app.screen._nodes[-1] == ultimate

    async with App().run_test() as pilot:
        # Mount a widget before -2, which is "before the penultimate".
        penpenultimate = Static(id="penpenultimate")
        await pilot.app.mount_all(widgets)
        await pilot.app.mount(penpenultimate, before=-2)
        assert pilot.app.screen._nodes[-3] == penpenultimate

    async with App().run_test() as pilot:
        # Mount a widget after -2, which is "before the end".
        penultimate = Static(id="penultimate")
        await pilot.app.mount_all(widgets)
        await pilot.app.mount(penultimate, after=-2)
        assert pilot.app.screen._nodes[-2] == penultimate

    async with App().run_test() as pilot:
        # Mount a widget before 0, which is "at the start".
        start = Static(id="start")
        await pilot.app.mount_all(widgets)
        await pilot.app.mount(start, before=0)
        assert pilot.app.screen._nodes[0] == start

    async with App().run_test() as pilot:
        # Mount a widget after 0. You get the idea...
        second = Static(id="second")
        await pilot.app.mount_all(widgets)
        await pilot.app.mount(second, after=0)
        assert pilot.app.screen._nodes[1] == second

    async with App().run_test() as pilot:
        # Mount a widget relative to another via query.
        queue_jumper = Static(id="queue-jumper")
        await pilot.app.mount_all(widgets)
        await pilot.app.mount(queue_jumper, after="#starter-5")
        assert pilot.app.screen._nodes[6] == queue_jumper

    async with App().run_test() as pilot:
        # Mount a widget relative to another via query.
        queue_jumper = Static(id="queue-jumper")
        await pilot.app.mount_all(widgets)
        await pilot.app.mount(queue_jumper, after=widgets[5])
        assert pilot.app.screen._nodes[6] == queue_jumper

    async with App().run_test() as pilot:
        # Make sure we get told off for trying to before and after.
        await pilot.app.mount_all(widgets)
        with pytest.raises(MountError):
            await pilot.app.mount(Static(), before=2, after=2)

    async with App().run_test() as pilot:
        # Make sure we get told off trying to mount relative to something
        # that isn't actually in the DOM.
        await pilot.app.mount_all(widgets)
        with pytest.raises(MountError):
            await pilot.app.mount(Static(), before=Static())
        with pytest.raises(MountError):
            await pilot.app.mount(Static(), after=Static())

    async with App().run_test() as pilot:
        # Make sure we get an error if we try and mount with a selector that
        # results in more than one hit.
        await pilot.app.mount_all(widgets)
        with pytest.raises(TooManyMatches):
            await pilot.app.mount(Static(), before="Static")


async def test_mount_error() -> None:
    """Mounting a widget on an un-mounted widget should raise an error."""
    app = App()
    async with app.run_test():
        with pytest.raises(MountError):
            widget = Widget()
            widget.mount(Static())
