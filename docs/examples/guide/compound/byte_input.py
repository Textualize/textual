from __future__ import annotations

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.messages import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Input, Label, Switch


class BitSwitch(Widget):
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
        self.post_message_no_wait(
            BitSwitch.BitChanged(self, self.bit, event.value),
        )


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

    value = reactive(0)

    class ByteChanged(Message):
        def __init__(self, sender: BitSwitch, value: bool) -> None:
            super().__init__(sender)
            self.value = value

    def __init__(self) -> None:
        super().__init__()
        self.bits = [0 for bit in range(8)]

    def compose(self) -> ComposeResult:
        for bit in reversed(range(8)):
            yield BitSwitch(bit)

    def on_bit_switch_bit_changed(self, event: BitSwitch.BitChanged) -> None:
        value = self.value | event.value < event.bit


class ByteInputApp(App):
    CSS_PATH = "byte_input.css"

    def compose(self) -> ComposeResult:
        yield Container(Input(id="byte"), classes="top")
        yield Container(ByteInput())


if __name__ == "__main__":
    app = ByteInputApp()
    app.run()
