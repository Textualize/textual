"""Unit tests aimed at testing the option list messages."""

from __future__ import annotations

from textual.app import App, ComposeResult
from textual.geometry import Offset
from textual.widgets import OptionList
from textual.widgets.option_list import Option


class OptionListApp(App[None]):
    """Test option list application."""

    def __init__(self) -> None:
        super().__init__()
        self.messages: list[tuple[str, str, int]] = []

    def compose(self) -> ComposeResult:
        yield OptionList(*[Option(str(n), id=str(n)) for n in range(10)])

    def _record(self, event: OptionList.OptionMessage) -> None:
        assert isinstance(event.option_id, str)
        assert event.option_list is event.control
        self.messages.append(
            (event.__class__.__name__, event.option_id, event.option_index)
        )

    def on_option_list_option_highlighted(
        self, event: OptionList.OptionHighlighted
    ) -> None:
        self._record(event)

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        self._record(event)


async def test_messages_on_startup() -> None:
    """There should be a highlighted message when a non-empty option list first starts up."""
    async with OptionListApp().run_test() as pilot:
        assert isinstance(pilot.app, OptionListApp)
        await pilot.pause()
        assert pilot.app.messages == [("OptionHighlighted", "0", 0)]


async def test_same_highlight_message() -> None:
    """Highlighting a highlight should result in no message."""
    async with OptionListApp().run_test() as pilot:
        assert isinstance(pilot.app, OptionListApp)
        await pilot.pause()
        pilot.app.query_one(OptionList).highlighted = 0
        await pilot.pause()
        assert pilot.app.messages == [("OptionHighlighted", "0", 0)]


async def test_highlight_disabled_option_no_message() -> None:
    """Highlighting a disabled option should result in no messages."""
    async with OptionListApp().run_test() as pilot:
        assert isinstance(pilot.app, OptionListApp)
        await pilot.pause()
        pilot.app.query_one(OptionList).disable_option("1")
        pilot.app.query_one(OptionList).highlighted = 1
        await pilot.pause()
        assert pilot.app.messages[1:] == []


async def test_new_highlight() -> None:
    """Setting the highlight to a new option should result in a message."""
    async with OptionListApp().run_test() as pilot:
        assert isinstance(pilot.app, OptionListApp)
        await pilot.pause()
        pilot.app.query_one(OptionList).highlighted = 2
        await pilot.pause()
        assert pilot.app.messages[1:] == [("OptionHighlighted", "2", 2)]


async def test_move_highlight_with_keyboard() -> None:
    """Changing option via the keyboard should result in a message."""
    async with OptionListApp().run_test() as pilot:
        assert isinstance(pilot.app, OptionListApp)
        await pilot.press("tab", "down")
        assert pilot.app.messages[1:] == [("OptionHighlighted", "1", 1)]


async def test_select_message_with_keyboard() -> None:
    """Hitting enter on an option should result in a message."""
    async with OptionListApp().run_test() as pilot:
        assert isinstance(pilot.app, OptionListApp)
        await pilot.press("tab", "down", "enter")
        assert pilot.app.messages[1:] == [
            ("OptionHighlighted", "1", 1),
            ("OptionSelected", "1", 1),
        ]


async def test_click_option_with_mouse() -> None:
    """Clicking on an option via the mouse should result in highlight and select messages."""
    async with OptionListApp().run_test() as pilot:
        assert isinstance(pilot.app, OptionListApp)
        await pilot.click(OptionList, Offset(2, 2))
        assert pilot.app.messages[1:] == [
            ("OptionHighlighted", "1", 1),
            ("OptionSelected", "1", 1),
        ]


async def test_click_disabled_option_with_mouse() -> None:
    """Clicking on a disabled option via the mouse should result no messages."""
    async with OptionListApp().run_test() as pilot:
        assert isinstance(pilot.app, OptionListApp)
        pilot.app.query_one(OptionList).disable_option("1")
        await pilot.click(OptionList, Offset(1, 1))
        assert pilot.app.messages[1:] == []
