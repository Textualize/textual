import threading

import pytest

from textual._dispatch_key import dispatch_key
from textual.app import App, ComposeResult
from textual.errors import DuplicateKeyHandlers
from textual.events import Key
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Button, Input, Label


class ValidWidget(Widget):
    called_by = None

    def key_x(self):
        self.called_by = self.key_x

    def key_ctrl_i(self):
        self.called_by = self.key_ctrl_i


async def test_dispatch_key_valid_key():
    widget = ValidWidget()
    result = await dispatch_key(widget, Key(key="x", character="x"))
    assert result is True
    assert widget.called_by == widget.key_x


async def test_dispatch_key_valid_key_alias():
    """When you press tab or ctrl+i, it comes through as a tab key event, but handlers for
    tab and ctrl+i are both considered valid."""
    widget = ValidWidget()
    result = await dispatch_key(widget, Key(key="tab", character="\t"))
    assert result is True
    assert widget.called_by == widget.key_ctrl_i


class DuplicateHandlersWidget(Widget):
    called_by = None

    def key_x(self):
        self.called_by = self.key_x

    def _key_x(self):
        self.called_by = self._key_x

    def key_tab(self):
        self.called_by = self.key_tab

    def key_ctrl_i(self):
        self.called_by = self.key_ctrl_i


async def test_dispatch_key_raises_when_conflicting_handler_aliases():
    """If you've got a handler for e.g. ctrl+i and a handler for tab, that's probably a mistake.
    In the terminal, they're the same thing, so we fail fast via exception here."""
    widget = DuplicateHandlersWidget()
    with pytest.raises(DuplicateKeyHandlers):
        await dispatch_key(widget, Key(key="tab", character="\t"))
    assert widget.called_by == widget.key_tab


class PreventTestApp(App):
    def __init__(self) -> None:
        self.input_changed_events = []
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Input()

    def on_input_changed(self, event: Input.Changed) -> None:
        self.input_changed_events.append(event)


async def test_message_queue_size():
    """Test message queue size property."""
    app = App()
    assert app.message_queue_size == 0

    class TestMessage(Message):
        pass

    async with app.run_test() as pilot:
        assert app.message_queue_size == 0
        app.post_message(TestMessage())
        assert app.message_queue_size == 1
        app.post_message(TestMessage())
        assert app.message_queue_size == 2
        # A pause will process all the messages
        await pilot.pause()
        assert app.message_queue_size == 0


async def test_prevent() -> None:
    app = PreventTestApp()

    async with app.run_test() as pilot:
        assert not app.input_changed_events
        input = app.query_one(Input)
        input.value = "foo"
        await pilot.pause()
        assert len(app.input_changed_events) == 1
        assert app.input_changed_events[0].value == "foo"

        with input.prevent(Input.Changed):
            input.value = "bar"

        await pilot.pause()
        assert len(app.input_changed_events) == 1
        assert app.input_changed_events[0].value == "foo"


async def test_prevent_with_call_next() -> None:
    """Test for https://github.com/Textualize/textual/issues/3166.

    Does a callback scheduled with `call_next` respect messages that
    were prevented when it was scheduled?
    """

    hits = 0

    class PreventTestApp(App[None]):
        def compose(self) -> ComposeResult:
            yield Input()

        def change_input(self) -> None:
            self.query_one(Input).value += "a"

        def on_input_changed(self) -> None:
            nonlocal hits
            hits += 1

    app = PreventTestApp()
    async with app.run_test() as pilot:
        app.call_next(app.change_input)
        await pilot.pause()
        assert hits == 1

        with app.prevent(Input.Changed):
            app.call_next(app.change_input)
        await pilot.pause()
        assert hits == 1

        app.call_next(app.change_input)
        await pilot.pause()
        assert hits == 2


async def test_prevent_default():
    """Test that prevent_default doesn't apply when a message is bubbled."""

    app_button_pressed = False

    class MyButton(Button):
        def _on_button_pressed(self, event: Button.Pressed) -> None:
            event.prevent_default()

    class PreventApp(App[None]):
        def compose(self) -> ComposeResult:
            yield MyButton("Press me")
            yield Label("No pressure")

        def on_button_pressed(self, event: Button.Pressed) -> None:
            nonlocal app_button_pressed
            app_button_pressed = True
            self.query_one(Label).update("Ouch!")

    app = PreventApp()
    async with app.run_test() as pilot:
        await pilot.click(MyButton)
        assert app_button_pressed


async def test_thread_safe_post_message():
    class TextMessage(Message):
        pass

    class TestApp(App):

        def on_mount(self) -> None:
            msg = TextMessage()
            threading.Thread(target=self.post_message, args=(msg,)).start()

        def on_text_message(self, message):
            self.exit()

    app = TestApp()

    async with app.run_test() as pilot:
        await pilot.pause()
