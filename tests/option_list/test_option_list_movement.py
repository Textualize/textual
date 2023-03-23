"""Test movement within an option list."""

from __future__ import annotations

from textual.app import App, ComposeResult
from textual.widgets import OptionList


class OptionListApp(App[None]):
    """Test option list application."""

    def compose(self) -> ComposeResult:
        yield OptionList("1", "2", "3", None, "4", "5", "6")


async def test_initial_highlight() -> None:
    """The highlight should start on the first item."""
    async with OptionListApp().run_test() as pilot:
        assert pilot.app.query_one(OptionList).highlighted == 0


async def test_cleared_highlight_is_none() -> None:
    """The highlight should be `None` if the list is cleared."""
    async with OptionListApp().run_test() as pilot:
        option_list = pilot.app.query_one(OptionList)
        option_list.clear()
        assert option_list.highlighted is None


async def test_cleared_movement_does_nothing() -> None:
    """The highlight should remain `None` if the list is cleared."""
    async with OptionListApp().run_test() as pilot:
        option_list = pilot.app.query_one(OptionList)
        option_list.clear()
        assert option_list.highlighted is None
        await pilot.press("tab", "down", "up", "page_down", "page_up", "home", "end")
        assert option_list.highlighted is None


async def test_move_down() -> None:
    """The highlight should move down when asked to."""
    async with OptionListApp().run_test() as pilot:
        await pilot.press("tab", "down")
        assert pilot.app.query_one(OptionList).highlighted == 1


async def test_move_down_from_end() -> None:
    """The highlight should wrap around when moving down from the end."""
    async with OptionListApp().run_test() as pilot:
        option_list = pilot.app.query_one(OptionList)
        option_list.highlighted = 5
        await pilot.press("tab", "down")
        assert option_list.highlighted == 0


async def test_move_up() -> None:
    """The highlight should move up when asked to."""
    async with OptionListApp().run_test() as pilot:
        option_list = pilot.app.query_one(OptionList)
        option_list.highlighted = 1
        await pilot.press("tab", "up")
        assert option_list.highlighted == 0


async def test_move_up_from_nowhere() -> None:
    """The highlight should settle on the last item when moving up from `None`."""
    async with OptionListApp().run_test() as pilot:
        await pilot.press("tab", "up")
        assert pilot.app.query_one(OptionList).highlighted == 5


async def test_move_end() -> None:
    """The end key should go to the end of the list."""
    async with OptionListApp().run_test() as pilot:
        await pilot.press("tab", "end")
        assert pilot.app.query_one(OptionList).highlighted == 5


async def test_move_home() -> None:
    """The home key should go to the start of the list."""
    async with OptionListApp().run_test() as pilot:
        option_list = pilot.app.query_one(OptionList)
        assert option_list.highlighted == 0
        option_list.highlighted = 5
        assert option_list.highlighted == 5
        await pilot.press("tab", "home")
        assert option_list.highlighted == 0
