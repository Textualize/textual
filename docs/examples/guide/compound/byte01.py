from __future__ import annotations

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.geometry import clamp
from textual.messages import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Input, Label, Switch


class BitSwitch(Widget):
    """A Switch with a numeric label above it."""

    DEFAULT_CSS = """
    BitSwitch {
        layout: vertical;
        width: auto;
        height: auto;
    }
    BitSwitch > Label {
        text-align: center;
        width: 1fr;
    }
    """

    class BitChanged(Message):
        """Sent when the 'bit' changes."""

        def __init__(self, sender: BitSwitch, bit: int, value: bool) -> None:
            super().__init__(sender)
            self.bit = bit
            self.value = value

    value = reactive(0)

    def __init__(self, bit: int) -> None:
        self.bit = bit
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Label(str(self.bit))
        yield Switch()

    def watch_value(self, value: bool) -> None:
        """When the value changes we want to set the switch accordingly."""
        self.query_one(Switch).value = value

    def on_switch_changed(self, event: Switch.Changed) -> None:
        """When the switch changes, notify the parent via a message."""
        event.stop()
        self.value = event.value
        self.post_message_no_wait(self.BitChanged(self, self.bit, event.value))


class ByteInputApp(App):
    def compose(self) -> ComposeResult:
        for bit_no in range(8):
            yield BitSwitch(bit_no)


if __name__ == "__main__":
    app = ByteInputApp()
    app.run()
