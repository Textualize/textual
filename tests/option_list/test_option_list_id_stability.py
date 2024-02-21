"""Tests inspired by https://github.com/Textualize/textual/issues/4101"""

from __future__ import annotations

from textual.app import App, ComposeResult
from textual.widgets import OptionList
from textual.widgets.option_list import Option


class OptionListApp(App[None]):
    """Test option list application."""

    def compose(self) -> ComposeResult:
        yield OptionList()


async def test_get_after_add() -> None:
    """It should be possible to get an option by ID after adding."""
    async with OptionListApp().run_test() as pilot:
        option_list = pilot.app.query_one(OptionList)
        option_list.add_option(Option("0", id="0"))
        assert option_list.get_option("0").id == "0"
