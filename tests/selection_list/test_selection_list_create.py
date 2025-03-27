"""Core selection list unit tests, aimed at testing basic list creation.

Note that the vast majority of the API *isn't* tested in here as
`SelectionList` inherits from `OptionList` and so that would be duplicated
effort. Instead these tests aim to just test the things that have been
changed or wrapped in some way.
"""

from __future__ import annotations

import pytest

from textual.app import App, ComposeResult
from textual.widgets import SelectionList
from textual.widgets.option_list import Option
from textual.widgets.selection_list import Selection, SelectionError


class SelectionListApp(App[None]):
    """Test selection list application."""

    def compose(self) -> ComposeResult:
        yield SelectionList[int](
            ("0", 0),
            ("1", 1, False),
            ("2", 2, True),
            Selection("3", 3, id="3"),
            Selection("4", 4, True, id="4"),
        )


async def test_all_parameters_become_selctions() -> None:
    """All input parameters to a list should become selections."""
    async with SelectionListApp().run_test() as pilot:
        selections = pilot.app.query_one(SelectionList)
        assert selections.option_count == 5
        for n in range(5):
            assert isinstance(selections.get_option_at_index(n), Selection)


async def test_get_selection_by_index() -> None:
    """It should be possible to get a selection by index."""
    async with SelectionListApp().run_test() as pilot:
        option_list = pilot.app.query_one(SelectionList)
        for n in range(5):
            assert str(option_list.get_option_at_index(n).prompt) == str(n)
        assert str(option_list.get_option_at_index(-1).prompt) == "4"


async def test_get_selection_by_id() -> None:
    """It should be possible to get a selection by ID."""
    async with SelectionListApp().run_test() as pilot:
        option_list = pilot.app.query_one(SelectionList)
        assert str(option_list.get_option("3").prompt) == "3"
        assert str(option_list.get_option("4").prompt) == "4"


async def test_add_later() -> None:
    """It should be possible to add more items to a selection list."""
    async with SelectionListApp().run_test() as pilot:
        selections = pilot.app.query_one(SelectionList)
        assert selections.option_count == 5
        selections.add_option(("5", 5))
        assert selections.option_count == 6
        selections.add_option(Selection("6", 6))
        assert selections.option_count == 7
        selections.add_options(
            [Selection("7", 7), Selection("8", 8, True), ("9", 9), ("10", 10, True)]
        )
        assert selections.option_count == 11
        selections.add_options([])
        assert selections.option_count == 11


async def test_add_later_selcted_state() -> None:
    """When adding selections later the selected collection should get updated."""
    async with SelectionListApp().run_test() as pilot:
        selections = pilot.app.query_one(SelectionList)
        assert selections.selected == [2, 4]
        selections.add_option(("5", 5, True))
        assert selections.selected == [2, 4, 5]
        selections.add_option(Selection("6", 6, True))
        assert selections.selected == [2, 4, 5, 6]


async def test_add_non_selections() -> None:
    """Adding options that aren't selections should result in errors."""
    async with SelectionListApp().run_test() as pilot:
        selections = pilot.app.query_one(SelectionList)
        with pytest.raises(SelectionError):
            selections.add_option(None)
        with pytest.raises(SelectionError):
            selections.add_option(Option("Nope"))
        with pytest.raises(SelectionError):
            selections.add_option("Nope")
        with pytest.raises(SelectionError):
            selections.add_option(("Nope",))
        with pytest.raises(SelectionError):
            selections.add_option(("Nope", 0, False, 23))


async def test_clear_options() -> None:
    """Clearing the options should also clear the selections."""
    async with SelectionListApp().run_test() as pilot:
        selections = pilot.app.query_one(SelectionList)
        selections.clear_options()
        assert selections.selected == []


async def test_options_are_available_soon() -> None:
    """Regression test for https://github.com/Textualize/textual/issues/3903."""

    selection = Selection("", 0, id="some_id")
    selection_list = SelectionList[int](selection)
    assert selection_list.get_option("some_id") is selection


async def test_removing_option_updates_indexes() -> None:
    async with SelectionListApp().run_test() as pilot:
        selections = pilot.app.query_one(SelectionList)
        assert selections._values == {n: n for n in range(5)}

        selections.remove_option_at_index(0)
        assert selections._values == {n + 1: n for n in range(4)}
