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
        option_list = pilot.app.query_one(OptionList)
        assert option_list.highlighted == 0


async def test_cleared_highlight_is_none() -> None:
    """The highlight should be `None` if the list is cleared."""
    async with OptionListApp().run_test() as pilot:
        option_list = pilot.app.query_one(OptionList)
        option_list.clear()
        assert option_list.highlighted is None


async def test_move_down() -> None:
    """The highlight should move down when asked to."""
    async with OptionListApp().run_test() as pilot:
        await pilot.press("tab", "down")
        option_list = pilot.app.query_one(OptionList)
        assert option_list.highlighted == 1


async def test_move_up() -> None:
    """The highlight should move up when asked to."""
    async with OptionListApp().run_test() as pilot:
        option_list = pilot.app.query_one(OptionList)
        option_list.highlighted = 1
        await pilot.press("tab", "up")
        assert option_list.highlighted == 0


# TODO: MORE
