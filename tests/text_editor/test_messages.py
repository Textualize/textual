from typing import List

from textual import on
from textual.app import App, ComposeResult
from textual.events import Event
from textual.message import Message
from textual.widgets import TextEditor


class TextEditorApp(App):
    def __init__(self):
        super().__init__()
        self.messages = []

    @on(TextEditor.Changed)
    @on(TextEditor.SelectionChanged)
    def message_received(self, message: Message):
        self.messages.append(message)

    def compose(self) -> ComposeResult:
        yield TextEditor("123")


def get_changed_messages(messages: List[Event]) -> List[TextEditor.Changed]:
    return [message for message in messages if isinstance(message, TextEditor.Changed)]


def get_selection_changed_messages(
    messages: List[Event],
) -> List[TextEditor.SelectionChanged]:
    return [
        message
        for message in messages
        if isinstance(message, TextEditor.SelectionChanged)
    ]


async def test_changed_message_edit_via_api():
    app = TextEditorApp()
    async with app.run_test() as pilot:
        text_editor = app.query_one(TextEditor)
        assert get_changed_messages(app.messages) == []

        text_editor.insert("A")
        await pilot.pause()

        assert get_changed_messages(app.messages) == [TextEditor.Changed(text_editor)]
        assert get_selection_changed_messages(app.messages) == [
            TextEditor.SelectionChanged(text_editor.selection, text_editor)
        ]


async def test_changed_message_via_typing():
    app = TextEditorApp()
    async with app.run_test() as pilot:
        text_editor = app.query_one(TextEditor)
        assert get_changed_messages(app.messages) == []

        await pilot.press("a")

        assert get_changed_messages(app.messages) == [TextEditor.Changed(text_editor)]
        assert get_selection_changed_messages(app.messages) == [
            TextEditor.SelectionChanged(text_editor.selection, text_editor)
        ]


async def test_selection_changed_via_api():
    app = TextEditorApp()
    async with app.run_test() as pilot:
        text_editor = app.query_one(TextEditor)
        assert get_selection_changed_messages(app.messages) == []

        text_editor.cursor_location = (0, 1)
        await pilot.pause()

        assert get_selection_changed_messages(app.messages) == [
            TextEditor.SelectionChanged(text_editor.selection, text_editor)
        ]


async def test_selection_changed_via_typing():
    app = TextEditorApp()
    async with app.run_test() as pilot:
        text_editor = app.query_one(TextEditor)
        assert get_selection_changed_messages(app.messages) == []

        await pilot.press("a")

        assert get_selection_changed_messages(app.messages) == [
            TextEditor.SelectionChanged(text_editor.selection, text_editor)
        ]
