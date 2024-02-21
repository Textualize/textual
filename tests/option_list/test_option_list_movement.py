"""Test movement within an option list."""

from __future__ import annotations

import pytest

from textual.app import App, ComposeResult
from textual.widgets import OptionList
from textual.widgets.option_list import Option


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
        option_list.clear_options()
        assert option_list.highlighted is None


async def test_cleared_movement_does_nothing() -> None:
    """The highlight should remain `None` if the list is cleared."""
    async with OptionListApp().run_test() as pilot:
        option_list = pilot.app.query_one(OptionList)
        option_list.clear_options()
        assert option_list.highlighted is None
        await pilot.press("tab", "down", "up", "pagedown", "pageup", "home", "end")
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


async def test_page_down_from_start_short_list() -> None:
    """Doing a page down from the start of a short list should move to the end."""
    async with OptionListApp().run_test() as pilot:
        await pilot.press("tab", "pagedown")
        assert pilot.app.query_one(OptionList).highlighted == 5


async def test_page_up_from_end_short_list() -> None:
    """Doing a page up from the end of a short list should move to the start."""
    async with OptionListApp().run_test() as pilot:
        option_list = pilot.app.query_one(OptionList)
        assert option_list.highlighted == 0
        option_list.highlighted = 5
        assert option_list.highlighted == 5
        await pilot.press("tab", "pageup")
        assert option_list.highlighted == 0


async def test_page_down_from_end_short_list() -> None:
    """Doing a page down from the end of a short list should go nowhere."""
    async with OptionListApp().run_test() as pilot:
        option_list = pilot.app.query_one(OptionList)
        assert option_list.highlighted == 0
        option_list.highlighted = 5
        assert option_list.highlighted == 5
        await pilot.press("tab", "pagedown")
        assert option_list.highlighted == 5


async def test_page_up_from_start_short_list() -> None:
    """Doing a page up from the start of a short list go nowhere."""
    async with OptionListApp().run_test() as pilot:
        await pilot.press("tab", "pageup")
        assert pilot.app.query_one(OptionList).highlighted == 0


class EmptyOptionListApp(App[None]):
    """Test option list application with no optons."""

    def compose(self) -> ComposeResult:
        yield OptionList()


async def test_empty_list_movement() -> None:
    """Attempting to move around an empty list should be a non-operation."""
    async with EmptyOptionListApp().run_test() as pilot:
        option_list = pilot.app.query_one(OptionList)
        await pilot.press("tab")
        for movement in ("up", "down", "home", "end", "pageup", "pagedown"):
            await pilot.press(movement)
            assert option_list.highlighted is None


@pytest.mark.parametrize(
    ["movement", "landing"],
    [
        ("up", 99),
        ("down", 0),
        ("home", 0),
        ("end", 99),
        ("pageup", 0),
        ("pagedown", 99),
    ],
)
async def test_no_highlight_movement(movement: str, landing: int) -> None:
    """Attempting to move around in a list with no highlight should select the most appropriate item."""
    async with EmptyOptionListApp().run_test() as pilot:
        option_list = pilot.app.query_one(OptionList)
        for _ in range(100):
            option_list.add_option("test")
        await pilot.press("tab")
        await pilot.press(movement)
        assert option_list.highlighted == landing


class OptionListDisabledOptionsApp(App[None]):
    def compose(self) -> ComposeResult:
        self.highlighted = []
        yield OptionList(
            Option("0", disabled=True),
            Option("1"),
            Option("2", disabled=True),
            Option("3", disabled=True),
            Option("4"),
            Option("5"),
            Option("6", disabled=True),
            Option("7"),
            Option("8", disabled=True),
        )

    def _on_option_list_option_highlighted(
        self, message: OptionList.OptionHighlighted
    ) -> None:
        self.highlighted.append(str(message.option.prompt))


async def test_keyboard_navigation_with_disabled_options() -> None:
    """Regression test for https://github.com/Textualize/textual/issues/3881."""

    app = OptionListDisabledOptionsApp()
    async with app.run_test() as pilot:
        for _ in range(5):
            await pilot.press("down")
        for _ in range(5):
            await pilot.press("up")

    assert app.highlighted == [
        "1",
        "4",
        "5",
        "7",
        "1",
        "4",
        "1",
        "7",
        "5",
        "4",
        "1",
    ]
