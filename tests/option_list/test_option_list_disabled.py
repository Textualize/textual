"""Unit tests for testing an option list's disabled facility."""

from __future__ import annotations

import pytest

from textual.app import App, ComposeResult
from textual.widgets import OptionList
from textual.widgets.option_list import Option, OptionDoesNotExist


class OptionListApp(App[None]):
    """Test option list application."""

    def __init__(self, disabled: bool) -> None:
        super().__init__()
        self.initial_disabled = disabled

    def compose(self) -> ComposeResult:
        """Compose the child widgets."""
        yield OptionList(
            *[
                Option(str(n), id=str(n), disabled=self.initial_disabled)
                for n in range(100)
            ]
        )


async def test_default_enabled() -> None:
    """Options created enabled should remain enabled."""
    async with OptionListApp(False).run_test() as pilot:
        option_list = pilot.app.query_one(OptionList)
        for option in range(option_list.option_count):
            assert option_list.get_option_at_index(option).disabled is False


async def test_default_disabled() -> None:
    """Options created disabled should remain disabled."""
    async with OptionListApp(True).run_test() as pilot:
        option_list = pilot.app.query_one(OptionList)
        for option in range(option_list.option_count):
            assert option_list.get_option_at_index(option).disabled is True


async def test_enabled_to_disabled_via_index() -> None:
    """It should be possible to change enabled to disabled via index."""
    async with OptionListApp(False).run_test() as pilot:
        option_list = pilot.app.query_one(OptionList)
        for n in range(option_list.option_count):
            assert option_list.get_option_at_index(n).disabled is False
            option_list.disable_option_at_index(n)
            assert option_list.get_option_at_index(n).disabled is True


async def test_disabled_to_enabled_via_index() -> None:
    """It should be possible to change disabled to enabled via index."""
    async with OptionListApp(True).run_test() as pilot:
        option_list = pilot.app.query_one(OptionList)
        for n in range(option_list.option_count):
            assert option_list.get_option_at_index(n).disabled is True
            option_list.enable_option_at_index(n)
            assert option_list.get_option_at_index(n).disabled is False


async def test_enabled_to_disabled_via_id() -> None:
    """It should be possible to change enabled to disabled via id."""
    async with OptionListApp(False).run_test() as pilot:
        option_list = pilot.app.query_one(OptionList)
        for n in range(option_list.option_count):
            assert option_list.get_option(str(n)).disabled is False
            option_list.disable_option(str(n))
            assert option_list.get_option(str(n)).disabled is True


async def test_disabled_to_enabled_via_id() -> None:
    """It should be possible to change disabled to enabled via id."""
    async with OptionListApp(True).run_test() as pilot:
        option_list = pilot.app.query_one(OptionList)
        for n in range(option_list.option_count):
            assert option_list.get_option(str(n)).disabled is True
            option_list.enable_option(str(n))
            assert option_list.get_option(str(n)).disabled is False


async def test_disable_invalid_id() -> None:
    """Disabling an option via an ID that does not exist should throw an error."""
    async with OptionListApp(True).run_test() as pilot:
        with pytest.raises(OptionDoesNotExist):
            pilot.app.query_one(OptionList).disable_option("does-not-exist")


async def test_disable_invalid_index() -> None:
    """Disabling an option via an index that does not exist should throw an error."""
    async with OptionListApp(True).run_test() as pilot:
        with pytest.raises(OptionDoesNotExist):
            pilot.app.query_one(OptionList).disable_option_at_index(4242)


async def test_enable_invalid_id() -> None:
    """Disabling an option via an ID that does not exist should throw an error."""
    async with OptionListApp(False).run_test() as pilot:
        with pytest.raises(OptionDoesNotExist):
            pilot.app.query_one(OptionList).enable_option("does-not-exist")


async def test_enable_invalid_index() -> None:
    """Disabling an option via an index that does not exist should throw an error."""
    async with OptionListApp(False).run_test() as pilot:
        with pytest.raises(OptionDoesNotExist):
            pilot.app.query_one(OptionList).enable_option_at_index(4242)
