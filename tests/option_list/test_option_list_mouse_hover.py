"""Unit tests aimed at checking the OptionList mouse hover handing."""

from __future__ import annotations

from textual.app import App, ComposeResult
from textual.geometry import Offset
from textual.widgets import Label, OptionList
from textual.widgets.option_list import Option


class OptionListApp(App[None]):
    """Test option list application."""

    def compose(self) -> ComposeResult:
        yield Label("Something else to hover over")
        yield OptionList(
            *[Option(str(n), id=str(n), disabled=n == 3) for n in range(10)]
        )


async def test_no_hover() -> None:
    """When the mouse isn't over the OptionList _mouse_hovering_over should be None."""
    async with OptionListApp().run_test() as pilot:
        await pilot.hover(Label)
        assert pilot.app.query_one(OptionList)._mouse_hovering_over is None


async def test_hover_highlight() -> None:
    """The mouse hover value should react to the mouse hover over a highlighted option."""
    async with OptionListApp().run_test() as pilot:
        await pilot.hover(OptionList, Offset(2, 1))
        option_list = pilot.app.query_one(OptionList)
        assert option_list._mouse_hovering_over == 0
        assert option_list._mouse_hovering_over == option_list.highlighted


async def test_hover_no_highlight() -> None:
    """The mouse hover value should react to the mouse hover over a non-highlighted option."""
    async with OptionListApp().run_test() as pilot:
        await pilot.hover(OptionList, Offset(1, 1) + Offset(2, 1))
        option_list = pilot.app.query_one(OptionList)
        assert option_list._mouse_hovering_over == 1
        assert option_list._mouse_hovering_over != option_list.highlighted


async def test_hover_disabled() -> None:
    """The mouse hover value should react to the mouse hover over a disabled option."""
    async with OptionListApp().run_test() as pilot:
        await pilot.hover(OptionList, Offset(1, 3) + Offset(2, 1))
        option_list = pilot.app.query_one(OptionList)
        assert option_list._mouse_hovering_over == 3
        assert option_list.get_option_at_index(
            option_list._mouse_hovering_over
        ).disabled
        assert option_list._mouse_hovering_over != option_list.highlighted


async def test_hover_then_leave() -> None:
    """After a mouse has been over an OptionList and left _mouse_hovering_over should be None again."""
    async with OptionListApp().run_test() as pilot:
        await pilot.hover(OptionList, Offset(2, 1))
        option_list = pilot.app.query_one(OptionList)
        assert option_list._mouse_hovering_over == 0
        await pilot.hover(Label)
        assert option_list._mouse_hovering_over is None
