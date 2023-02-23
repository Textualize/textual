from __future__ import annotations

from textual.app import App, ComposeResult
from textual.containers import Container
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
        def __init__(self, sender: BitSwitch, bit: int, value: bool) -> None:
            super().__init__(sender)
            self.bit = bit
            self.value = value

    value = reactive(False)

    def __init__(self, bit: int) -> None:
        self.bit = bit
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Label(str(self.bit))
        yield Switch()

    def watch_value(self, value: bool) -> None:
        self.query_one(Switch).value = value

    def on_switch_changed(self, event: Switch.Changed) -> None:
        event.stop()
        self.value = event.value
        self.post_message_no_wait(self.BitChanged(self, self.bit, event.value))


class ByteInput(Widget):
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
    """

    value = reactive(0)

    def validate_value(self, value: int) -> int:
        if value > 255:
            return 255
        if value < 0:
            return 0
        return value

    def compose(self) -> ComposeResult:
        yield Container(Input(id="byte"), classes="top")
        yield Container(ByteInput())

    def on_bit_switch_bit_changed(self, event: BitSwitch.BitChanged) -> None:
        print("!!!", event)
        value = 0
        for switch in self.query(BitSwitch):
            value |= switch.value << switch.bit
        self.query_one(Input).value = str(value or "")

    def watch_value(self, value: int) -> None:
        self.update_switches(value)

    def update_switches(self, byte: int) -> None:
        for switch in self.query(BitSwitch):
            with switch.prevent(BitSwitch.BitChanged):
                switch.value = bool(byte & (1 << switch.bit))

    def on_input_changed(self, event: Input.Changed) -> None:
        try:
            byte = int(event.value or "0")
        except ValueError:
            pass
        else:
            self.value = byte


class ByteInputApp(App):
    def compose(self) -> ComposeResult:
        yield ByteEditor()


if __name__ == "__main__":
    app = ByteInputApp()
    app.run()
