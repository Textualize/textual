"""Tests for the tooltips."""

from typing_extensions import Final

from textual.app import App, ComposeResult
from textual.widgets import Static


class TooltipApp(App[None]):

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


TOOLTIP_TIMEOUT: Final[float] = 0.3


async def test_no_tip_gets_no_tooltip() -> None:
    """If there is no tooltip, none should show."""
    async with TooltipApp().run_test(tooltips=True) as pilot:
        assert pilot.app.query_one("#textual-tooltip").display is False
        await pilot.hover("#mr-pink")
        assert pilot.app.query_one("#textual-tooltip").display is False
        await pilot.pause(TOOLTIP_TIMEOUT * 2)
        assert pilot.app.query_one("#textual-tooltip").display is False


async def test_tip_gets_a_tooltip() -> None:
    """If there is a tooltip, it should show."""
    async with TooltipApp().run_test(tooltips=True) as pilot:
        assert pilot.app.query_one("#textual-tooltip").display is False
        await pilot.hover("#mr-blue")
        assert pilot.app.query_one("#textual-tooltip").display is False
        await pilot.pause(TOOLTIP_TIMEOUT * 2)
        assert pilot.app.query_one("#textual-tooltip").display is True
