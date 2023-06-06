from __future__ import annotations

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.geometry import clamp
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

    value = reactive(0)

    def __init__(self, bit: int) -> None:
        self.bit = bit
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Label(str(self.bit))
        yield Switch()

    def watch_value(self, value: bool) -> None:  # (1)!
        """When the value changes we want to set the switch accordingly."""
        self.query_one(Switch).value = value

    def on_switch_changed(self, event: Switch.Changed) -> None:
        """When the switch changes, notify the parent via a message."""
        event.stop()
        self.value = event.value
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

    value = reactive(0)

    def validate_value(self, value: int) -> int:  # (2)!
        """Ensure value is between 0 and 255."""
        return clamp(value, 0, 255)

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

    def on_input_changed(self, event: Input.Changed) -> None:  # (3)!
        """When the text changes, set the value of the byte."""
        try:
            self.value = int(event.value or "0")
        except ValueError:
            pass

    def watch_value(self, value: int) -> None:  # (4)!
        """When self.value changes, update switches."""
        for switch in self.query(BitSwitch):
            with switch.prevent(BitSwitch.BitChanged):  # (5)!
                switch.value = bool(value & (1 << switch.bit))  # (6)!


class ByteInputApp(App):
    def compose(self) -> ComposeResult:
        yield ByteEditor()


if __name__ == "__main__":
    app = ByteInputApp()
    app.run()
