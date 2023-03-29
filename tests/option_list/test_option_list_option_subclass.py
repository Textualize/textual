"""Unit tests aimed at ensuring the option list option class can be subclassed."""

from __future__ import annotations

from textual.app import App, ComposeResult
from textual.widgets import OptionList
from textual.widgets.option_list import Option


class OptionWithExtras(Option):
    """An example subclass of a option."""

    def __init__(self, test: int) -> None:
        super().__init__(str(test), str(test), False)
        self.test = test


class OptionListApp(App[None]):
    """Test option list application."""

    def compose(self) -> ComposeResult:
        yield OptionList(*[OptionWithExtras(n) for n in range(100)])


async def test_option_list_with_subclassed_options() -> None:
    """It should be possible to build an option list with subclassed options."""
    async with OptionListApp().run_test() as pilot:
        option_list = pilot.app.query_one(OptionList)
        assert option_list.option_count == 100
        for n in range(option_list.option_count):
            for option in (
                option_list.get_option(str(n)),
                option_list.get_option_at_index(n),
            ):
                assert isinstance(option, OptionWithExtras)
                assert option.prompt == str(n)
                assert option.id == str(n)
                assert option.test == n
