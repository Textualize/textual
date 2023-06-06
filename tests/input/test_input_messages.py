from __future__ import annotations

from textual import on
from textual.app import App, ComposeResult
from textual.events import Paste
from textual.widgets import Input


class InputApp(App[None]):
    def __init__(self, initial: str | None = None) -> None:
        super().__init__()
        self.messages: list[str] = []
        self._initial = initial

    def compose(self) -> ComposeResult:
        if self._initial:
            yield Input(self._initial)
        else:
            yield Input()

    @on(Input.Changed)
    @on(Input.Submitted)
    def log_message(self, event: Input.Submitted | Input.Changed) -> None:
        assert event.control == event.input
        self.messages.append(event.__class__.__name__)


async def test_no_startup_messages():
    """An input with no initial value should have no initial messages."""
    async with InputApp().run_test() as pilot:
        assert pilot.app.messages == []


async def test_startup_messages_with_initial_value():
    """An input with an initial value should send a changed event."""
    async with InputApp("Hello, World!").run_test() as pilot:
        assert pilot.app.messages == ["Changed"]


async def test_typing_from_empty_causes_changed():
    """An input with no initial value should send messages when entering text."""
    input_text = "Hello, World!"
    async with InputApp().run_test() as pilot:
        await pilot.press(*input_text)
        assert pilot.app.messages == ["Changed"] * len(input_text)


async def test_typing_from_pre_populated_causes_changed():
    """An input with initial value should send messages when entering text after an initial message."""
    input_text = "Hello, World!"
    async with InputApp(input_text).run_test() as pilot:
        await pilot.press(*input_text)
        assert pilot.app.messages == ["Changed"] + (["Changed"] * len(input_text))


async def test_submit_empty_input():
    """Pressing enter on an empty input should send a submitted event."""
    async with InputApp().run_test() as pilot:
        await pilot.press("enter")
        assert pilot.app.messages == ["Submitted"]


async def test_submit_pre_populated_input():
    """Pressing enter on a pre-populated input should send a changed then submitted event."""
    async with InputApp("The owls are not what they seem").run_test() as pilot:
        await pilot.press("enter")
        assert pilot.app.messages == ["Changed", "Submitted"]


async def test_paste_event_impact():
    """A paste event should result in a changed event."""
    async with InputApp().run_test() as pilot:
        await pilot.app._post_message(Paste("Hello, World"))
        await pilot.pause()
        assert pilot.app.messages == ["Changed"]
