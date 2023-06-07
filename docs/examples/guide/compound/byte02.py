from __future__ import annotations

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.message import Message
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
        width: 100%;
    }
    """

    class BitChanged(Message):
        """Sent when the 'bit' changes."""

        def __init__(self, bit: int, value: bool) -> None:
            super().__init__()
            self.bit = bit
            self.value = value

    value = reactive(0)  # (1)!

    def __init__(self, bit: int) -> None:
        self.bit = bit
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Label(str(self.bit))
        yield Switch()

    def on_switch_changed(self, event: Switch.Changed) -> None:  # (2)!
        """When the switch changes, notify the parent via a message."""
        event.stop()  # (3)!
        self.value = event.value  # (4)!
        self.post_message(self.BitChanged(self.bit, event.value))


class ByteInput(Widget):
    """A compound widget with 8 switches."""

    DEFAULT_CSS = """
    ByteInput {
        width: auto;
        height: auto;
        border: blank;
        layout: horizontal;
    }
    ByteInput:focus-within {
        border: heavy $secondary;
    }
    """

    def compose(self) -> ComposeResult:
        for bit in reversed(range(8)):
            yield BitSwitch(bit)


class ByteEditor(Widget):
    DEFAULT_CSS = """
    ByteEditor > Container {
        height: 1fr;
        align: center middle;
    }
    ByteEditor > Container.top {
        background: $boost;
    }
    ByteEditor Input {
        width: 16;
    }
    """

    def compose(self) -> ComposeResult:
        with Container(classes="top"):
            yield Input(placeholder="byte")
        with Container():
            yield ByteInput()

    def on_bit_switch_bit_changed(self, event: BitSwitch.BitChanged) -> None:
        """When a switch changes, update the value."""
        value = 0
        for switch in self.query(BitSwitch):
            value |= switch.value << switch.bit
        self.query_one(Input).value = str(value)


class ByteInputApp(App):
    def compose(self) -> ComposeResult:
        yield ByteEditor()


if __name__ == "__main__":
    app = ByteInputApp()
    app.run()
