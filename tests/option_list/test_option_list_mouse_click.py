from __future__ import annotations

from textual import on
from textual.app import App, ComposeResult
from textual.widgets import OptionList
from textual.widgets.option_list import Option


class OptionListApp(App[None]):
    messages: list[str] = []

    def compose(self) -> ComposeResult:
        yield OptionList(
            Option("0"),
            None,
            Option("1"),
        )

    @on(OptionList.OptionMessage)
    def log_option_message(
        self,
        event: OptionList.OptionMessage,
    ) -> None:
        self.messages.append(event.__class__.__name__)


async def test_option_list_clicking_separator() -> None:
    """Regression test for https://github.com/Textualize/textual/issues/4710"""
    app = OptionListApp()
    async with app.run_test() as pilot:
        option_list = pilot.app.query_one(OptionList)
        expected_messages = ["OptionHighlighted"]  # Initial highlight
        assert option_list.highlighted == 0
        assert app.messages == expected_messages

        # Select the second option with the mouse
        await pilot.click(OptionList, offset=(3, 3))
        expected_messages.extend(["OptionHighlighted", "OptionSelected"])
        assert option_list.highlighted == 1
        assert app.messages == expected_messages

        # Click the separator - there should be no change
        await pilot.click(OptionList, offset=(3, 2))
        assert option_list.highlighted == 1
        assert app.messages == expected_messages
