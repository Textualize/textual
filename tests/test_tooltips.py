"""Tests for the tooltips."""

from typing_extensions import Final

from textual.app import App, ComposeResult
from textual.widgets import Static


class TooltipApp(App[None]):
    TOOLTIP_DELAY = 0.4
    CSS = """
    Static {
        width: 1fr;
        height: 1fr;
    }
    """

    @staticmethod
    def tip(static: Static) -> Static:
        static.tooltip = "This is a test tooltip"
        return static

    def compose(self) -> ComposeResult:
        yield Static(id="mr-pink")
        yield self.tip(Static(id="mr-blue"))


TOOLTIP_TIMEOUT: Final[float] = 0.4 + 0.1
"""How long to wait for a tooltip to appear.

The 0.4 is the value defined with TOOLTIP_DELAY, and the 0.1 is a bit of
wiggle room.
"""


async def test_no_tip_gets_no_tooltip() -> None:
    """If there is no tooltip, none should show."""
    async with TooltipApp().run_test(tooltips=True) as pilot:
        assert pilot.app.query_one("#textual-tooltip").display is False
        await pilot.hover("#mr-pink")
        assert pilot.app.query_one("#textual-tooltip").display is False
        await pilot.pause(TOOLTIP_TIMEOUT)
        assert pilot.app.query_one("#textual-tooltip").display is False


async def test_tip_gets_a_tooltip() -> None:
    """If there is a tooltip, it should show."""
    async with TooltipApp().run_test(tooltips=True) as pilot:
        assert pilot.app.query_one("#textual-tooltip").display is False
        await pilot.hover("#mr-blue")
        assert pilot.app.query_one("#textual-tooltip").display is False
        await pilot.pause(TOOLTIP_TIMEOUT)
        assert pilot.app.query_one("#textual-tooltip").display is True


async def test_mouse_move_removes_a_tooltip() -> None:
    """If there is a mouse move when there is a tooltip, it should disappear."""
    async with TooltipApp().run_test(tooltips=True) as pilot:
        assert pilot.app.query_one("#textual-tooltip").display is False
        await pilot.hover("#mr-blue")
        assert pilot.app.query_one("#textual-tooltip").display is False
        await pilot.pause(TOOLTIP_TIMEOUT)
        assert pilot.app.query_one("#textual-tooltip").display is True
        await pilot.hover("#mr-pink")
        await pilot.pause(TOOLTIP_TIMEOUT)
        assert pilot.app.query_one("#textual-tooltip").display is False


async def test_removing_tipper_should_remove_tooltip() -> None:
    """If the tipping widget is removed, it should remove the tooltip."""
    async with TooltipApp().run_test(tooltips=True) as pilot:
        assert pilot.app.query_one("#textual-tooltip").display is False
        await pilot.hover("#mr-blue")
        assert pilot.app.query_one("#textual-tooltip").display is False
        await pilot.pause(TOOLTIP_TIMEOUT)
        assert pilot.app.query_one("#textual-tooltip").display is True
        await pilot.app.query_one("#mr-blue").remove()
        await pilot.pause()
        assert pilot.app.query_one("#textual-tooltip").display is False


async def test_making_tipper_invisible_should_remove_tooltip() -> None:
    """If the tipping widget is made invisible, it should remove the tooltip."""
    async with TooltipApp().run_test(tooltips=True) as pilot:
        assert pilot.app.query_one("#textual-tooltip").display is False
        await pilot.hover("#mr-blue")
        assert pilot.app.query_one("#textual-tooltip").display is False
        await pilot.pause(TOOLTIP_TIMEOUT)
        assert pilot.app.query_one("#textual-tooltip").display is True
        pilot.app.query_one("#mr-blue").visible = False
        await pilot.pause()
        assert pilot.app.query_one("#textual-tooltip").display is False


async def test_making_tipper_not_displayed_should_remove_tooltip() -> None:
    """If the tipping widget is made display none, it should remove the tooltip."""
    async with TooltipApp().run_test(tooltips=True) as pilot:
        assert pilot.app.query_one("#textual-tooltip").display is False
        await pilot.hover("#mr-blue")
        assert pilot.app.query_one("#textual-tooltip").display is False
        await pilot.pause(TOOLTIP_TIMEOUT)
        assert pilot.app.query_one("#textual-tooltip").display is True
        pilot.app.query_one("#mr-blue").display = False
        await pilot.pause()
        assert pilot.app.query_one("#textual-tooltip").display is False


async def test_making_tipper_shuffle_away_should_remove_tooltip() -> None:
    """If the tipping widget moves from under the cursor, it should remove the tooltip."""
    async with TooltipApp().run_test(tooltips=True) as pilot:
        assert pilot.app.query_one("#textual-tooltip").display is False
        await pilot.hover("#mr-blue")
        assert pilot.app.query_one("#textual-tooltip").display is False
        await pilot.pause(TOOLTIP_TIMEOUT)
        assert pilot.app.query_one("#textual-tooltip").display is True
        await pilot.app.mount(Static(id="mr-brown"), before="#mr-blue")
        await pilot.pause()
        assert pilot.app.query_one("#textual-tooltip").display is False
