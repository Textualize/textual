import pytest

from textual.errors import DuplicateKeyHandlers
from textual.events import Key
from textual.widget import Widget


class ValidWidget(Widget):
    called_by = None

    def key_x(self):
        self.called_by = self.key_x

    def key_ctrl_i(self):
        self.called_by = self.key_ctrl_i


async def test_dispatch_key_valid_key():
    widget = ValidWidget()
    result = await widget.dispatch_key(Key(widget, key="x", char="x"))
    assert result is True
    assert widget.called_by == widget.key_x


async def test_dispatch_key_valid_key_alias():
    """When you press tab or ctrl+i, it comes through as a tab key event, but handlers for
    tab and ctrl+i are both considered valid."""
    widget = ValidWidget()
    result = await widget.dispatch_key(Key(widget, key="tab", char="\t"))
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
        await widget.dispatch_key(Key(widget, key="tab", char="\t"))
    assert widget.called_by == widget.key_tab
