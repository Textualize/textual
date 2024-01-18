"""Core option list unit tests, aimed at testing basic list creation."""

from __future__ import annotations

import pytest

from textual.app import App, ComposeResult
from textual.widgets import OptionList
from textual.widgets.option_list import (
    DuplicateID,
    Option,
    OptionDoesNotExist,
    Separator,
)


class OptionListApp(App[None]):
    """Test option list application."""

    def compose(self) -> ComposeResult:
        yield OptionList(
            "0",
            Option("1"),
            Separator(),
            Option("2", disabled=True),
            None,
            Option("3", id="3"),
            Option("4", id="4", disabled=True),
        )


async def test_all_parameters_become_options() -> None:
    """All input parameters to a list should become options."""
    async with OptionListApp().run_test() as pilot:
        option_list = pilot.app.query_one(OptionList)
        assert option_list.option_count == 5
        for n in range(5):
            assert isinstance(option_list.get_option_at_index(n), Option)


async def test_id_capture() -> None:
    """All options given an ID should retain the ID."""
    async with OptionListApp().run_test() as pilot:
        option_list = pilot.app.query_one(OptionList)
        with_id = 0
        without_id = 0
        for n in range(5):
            if option_list.get_option_at_index(n).id is None:
                without_id += 1
            else:
                with_id += 1
        assert with_id == 2
        assert without_id == 3


async def test_get_option_by_id() -> None:
    """It should be possible to get an option by ID."""
    async with OptionListApp().run_test() as pilot:
        option_list = pilot.app.query_one(OptionList)
        assert option_list.get_option("3").prompt == "3"
        assert option_list.get_option("4").prompt == "4"


async def test_get_option_with_bad_id() -> None:
    """Asking for an option with a bad ID should give an error."""
    async with OptionListApp().run_test() as pilot:
        with pytest.raises(OptionDoesNotExist):
            _ = pilot.app.query_one(OptionList).get_option("this does not exist")


async def test_get_option_by_index() -> None:
    """It should be possible to get an option by index."""
    async with OptionListApp().run_test() as pilot:
        option_list = pilot.app.query_one(OptionList)
        for n in range(5):
            assert option_list.get_option_at_index(n).prompt == str(n)
        assert option_list.get_option_at_index(-1).prompt == "4"


async def test_get_option_at_bad_index() -> None:
    """Asking for an option at a bad index should give an error."""
    async with OptionListApp().run_test() as pilot:
        with pytest.raises(OptionDoesNotExist):
            _ = pilot.app.query_one(OptionList).get_option_at_index(42)
        with pytest.raises(OptionDoesNotExist):
            _ = pilot.app.query_one(OptionList).get_option_at_index(-42)


async def test_clear_option_list() -> None:
    """It should be possible to clear the option list of all content."""
    async with OptionListApp().run_test() as pilot:
        option_list = pilot.app.query_one(OptionList)
        assert option_list.option_count == 5
        option_list.clear_options()
        assert option_list.option_count == 0


async def test_add_later() -> None:
    """It should be possible to add more items to a list."""
    async with OptionListApp().run_test() as pilot:
        option_list = pilot.app.query_one(OptionList)
        assert option_list.option_count == 5
        option_list.add_option("more")
        assert option_list.option_count == 6
        option_list.add_option()
        assert option_list.option_count == 6
        option_list.add_option(Option("even more"))
        assert option_list.option_count == 7
        option_list.add_options(
            [Option("more still"), "Yet more options", "so many options!"]
        )
        assert option_list.option_count == 10
        option_list.add_option(None)
        assert option_list.option_count == 10
        option_list.add_options([])
        assert option_list.option_count == 10


async def test_create_with_duplicate_id() -> None:
    """Adding an option with a duplicate ID should be an error."""
    async with OptionListApp().run_test() as pilot:
        option_list = pilot.app.query_one(OptionList)
        assert option_list.option_count == 5
        with pytest.raises(DuplicateID):
            option_list.add_option(Option("dupe", id="3"))
        assert option_list.option_count == 5


async def test_create_with_duplicate_id_and_subsequent_non_dupes() -> None:
    """Adding an option with a duplicate ID should be an error."""
    async with OptionListApp().run_test() as pilot:
        option_list = pilot.app.query_one(OptionList)
        assert option_list.option_count == 5
        with pytest.raises(DuplicateID):
            option_list.add_option(Option("dupe", id="3"))
        assert option_list.option_count == 5
        option_list.add_option(Option("Not a dupe", id="6"))
        assert option_list.option_count == 6
        option_list.add_option(Option("Not a dupe", id="7"))
        assert option_list.option_count == 7


async def test_adding_multiple_duplicates_at_once() -> None:
    """Adding duplicates together than aren't existing duplicates should be an error."""
    async with OptionListApp().run_test() as pilot:
        option_list = pilot.app.query_one(OptionList)
        assert option_list.option_count == 5
        with pytest.raises(DuplicateID):
            option_list.add_options(
                [
                    Option("dupe", id="42"),
                    Option("dupe", id="42"),
                ]
            )
        assert option_list.option_count == 5


async def test_options_are_available_soon() -> None:
    """Regression test for https://github.com/Textualize/textual/issues/3903."""

    option = Option("", id="some_id")
    option_list = OptionList(option)
    assert option_list.get_option("some_id") is option
