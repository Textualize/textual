from typing import List

from textual import on
from textual.app import App, ComposeResult
from textual.events import Event
from textual.message import Message
from textual.widgets import TextArea


class TextAreaApp(App):
    def __init__(self):
        super().__init__()
        self.messages = []

    @on(TextArea.Changed)
    @on(TextArea.SelectionChanged)
    def message_received(self, message: Message):
        self.messages.append(message)

    def compose(self) -> ComposeResult:
        yield TextArea("123")


def get_changed_messages(messages: List[Event]) -> List[TextArea.Changed]:
    return [message for message in messages if isinstance(message, TextArea.Changed)]


def get_selection_changed_messages(
    messages: List[Event],
) -> List[TextArea.SelectionChanged]:
    return [
        message
        for message in messages
        if isinstance(message, TextArea.SelectionChanged)
    ]


async def test_changed_message_edit_via_api():
    app = TextAreaApp()
    async with app.run_test() as pilot:
        text_area = app.query_one(TextArea)
        assert get_changed_messages(app.messages) == []

        text_area.insert("A")
        await pilot.pause()

        assert get_changed_messages(app.messages) == [TextArea.Changed(text_area)]
        assert get_selection_changed_messages(app.messages) == [
            TextArea.SelectionChanged(text_area.selection, text_area)
        ]


async def test_changed_message_via_typing():
    app = TextAreaApp()
    async with app.run_test() as pilot:
        text_area = app.query_one(TextArea)
        assert get_changed_messages(app.messages) == []

        await pilot.press("a")

        assert get_changed_messages(app.messages) == [TextArea.Changed(text_area)]
        assert get_selection_changed_messages(app.messages) == [
            TextArea.SelectionChanged(text_area.selection, text_area)
        ]


async def test_changed_message_edit_via_assignment():
    app = TextAreaApp()
    async with app.run_test() as pilot:
        text_area = app.query_one(TextArea)
        assert get_changed_messages(app.messages) == []

        text_area.text = ""
        await pilot.pause()

        assert get_changed_messages(app.messages) == [TextArea.Changed(text_area)]
        assert get_selection_changed_messages(app.messages) == []


async def test_selection_changed_via_api():
    app = TextAreaApp()
    async with app.run_test() as pilot:
        text_area = app.query_one(TextArea)
        assert get_selection_changed_messages(app.messages) == []

        text_area.cursor_location = (0, 1)
        await pilot.pause()

        assert get_selection_changed_messages(app.messages) == [
            TextArea.SelectionChanged(text_area.selection, text_area)
        ]


async def test_selection_changed_via_typing():
    app = TextAreaApp()
    async with app.run_test() as pilot:
        text_area = app.query_one(TextArea)
        assert get_selection_changed_messages(app.messages) == []

        await pilot.press("a")

        assert get_selection_changed_messages(app.messages) == [
            TextArea.SelectionChanged(text_area.selection, text_area)
        ]
