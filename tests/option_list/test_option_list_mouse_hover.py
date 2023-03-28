"""Unit tests aimed at checking the OptionList mouse hover handing."""

from __future__ import annotations

from textual.app import App, ComposeResult
from textual.widgets import Label, OptionList
from textual.widgets.option_list import Option


class OptionListApp(App[None]):
    """Test option list application."""

    def compose(self) -> ComposeResult:
        yield Label("Something else to hover over")
        yield OptionList(*[Option(str(n), id=str(n)) for n in range(10)])


async def test_no_hover() -> None:
    """When the mouse isn't over the OptionList mouse_hovering_over should be None."""
    async with OptionListApp().run_test() as pilot:
        await pilot.hover(Label)
        assert pilot.app.query_one(OptionList).mouse_hovering_over is None


async def test_hover() -> None:
    """The mouse hover reactive should react to the mouse hover."""
    async with OptionListApp().run_test() as pilot:
        await pilot.hover(OptionList)
        assert pilot.app.query_one(OptionList).mouse_hovering_over == 0


async def test_hover_then_leave() -> None:
    """After a mouse has been over an OptionList and left mouse_hovering_over should be None again."""
    async with OptionListApp().run_test() as pilot:
        await pilot.hover(OptionList)
        assert pilot.app.query_one(OptionList).mouse_hovering_over == 0
        await pilot.hover(Label)
        assert pilot.app.query_one(OptionList).mouse_hovering_over is None
