import pytest

from textual.app import App, ComposeResult
from textual.errors import DuplicateKeyHandlers
from textual.events import Key
from textual.widget import Widget
from textual.widgets import Input


class ValidWidget(Widget):
    called_by = None

    def key_x(self):
        self.called_by = self.key_x

    def key_ctrl_i(self):
        self.called_by = self.key_ctrl_i


async def test_dispatch_key_valid_key():
    widget = ValidWidget()
    result = await widget.dispatch_key(Key(widget, key="x", character="x"))
    assert result is True
    assert widget.called_by == widget.key_x


async def test_dispatch_key_valid_key_alias():
    """When you press tab or ctrl+i, it comes through as a tab key event, but handlers for
    tab and ctrl+i are both considered valid."""
    widget = ValidWidget()
    result = await widget.dispatch_key(Key(widget, key="tab", character="\t"))
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
        await widget.dispatch_key(Key(widget, key="tab", character="\t"))
    assert widget.called_by == widget.key_tab


class PreventTestApp(App):
    def __init__(self) -> None:
        self.input_changed_events = []
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Input()

    def on_input_changed(self, event: Input.Changed) -> None:
        self.input_changed_events.append(event)


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
