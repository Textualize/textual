from __future__ import annotations

from rich.console import RenderableType
from rich.text import Text

from textual import events
from textual._types import MessageTarget
from textual.geometry import Size
from textual.keys import Keys
from textual.message import Message
from textual.reactive import Reactive
from textual.widget import Widget


class TextInputBase(Widget):
    ALLOW_PROPAGATE = {}

    current_text = Reactive("", layout=True)
    cursor_index = Reactive(0)

    def on_key(self, event: events.Key) -> None:
        key = event.key

        if key == "\x1b":
            return

        changed = False
        if key == "ctrl+h" and self.cursor_index != 0:
            new_text = (
                self.current_text[: self.cursor_index - 1]
                + self.current_text[self.cursor_index :]
            )
            self.current_text = new_text
            self.cursor_index = max(0, self.cursor_index - 1)
            changed = True
        elif key == "ctrl+d" and self.cursor_index != len(self.current_text):
            new_text = (
                self.current_text[: self.cursor_index]
                + self.current_text[self.cursor_index + 1 :]
            )
            self.current_text = new_text
            changed = True
        elif key == "left":
            self.cursor_index = max(0, self.cursor_index - 1)
        elif key == "right":
            self.cursor_index = min(len(self.current_text), self.cursor_index + 1)
        elif key == "home":
            self.cursor_index = 0
        elif key == "end":
            self.cursor_index = len(self.current_text)
        elif key not in Keys.values():
            new_text = (
                self.current_text[: self.cursor_index]
                + key
                + self.current_text[self.cursor_index :]
            )
            self.current_text = new_text
            self.cursor_index = min(len(self.current_text), self.cursor_index + 1)
            changed = True

        if changed:
            self.post_message_no_wait(self.Changed(self, value=self.current_text))


class TextInput(TextInputBase, can_focus=True):

    ALLOW_PROPAGATE = {"tab", "shift+tab"}

    CSS = """
    TextInput {
        width: auto;
        background: $primary;
        height: 3;
        padding: 0 1;
        content-align: left middle;
    }

    TextInput:hover {
        background: $primary-darken-1;
    }

    TextInput:focus {
        background: $primary-darken-2;
        border: solid $primary-lighten-1;
        padding: 0;
    }

    App.-show-focus TextInput:focus {
        tint: $accent 20%;
    }
    """

    def __init__(
        self,
        placeholder: str = "",
        initial: str = "",
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ):
        super().__init__(name=name, id=id, classes=classes)
        self.placeholder = placeholder
        self.current_text = initial if initial else ""

    def get_content_width(self, container_size: Size, viewport_size: Size) -> int:
        return (
            max(len(self.current_text), len(self.placeholder))
            + self.styles.gutter.width
        )

    def render(self) -> RenderableType:
        # We only show the cursor if the widget has focus
        show_cursor = self.has_focus
        if self.current_text:
            display_text = Text(self.current_text, no_wrap=True)

            if show_cursor:
                display_text = self._apply_cursor_to_text(
                    display_text, self.cursor_index
                )
            return display_text
        else:
            # The user has not entered text - show the placeholder
            display_text = Text(self.placeholder, "dim")
            if show_cursor:
                display_text = self._apply_cursor_to_text(display_text, 0)
            return display_text

    def _apply_cursor_to_text(self, display_text: Text, index: int):
        # Either write a cursor character or apply reverse style to cursor location
        if index == len(display_text):
            display_text += "█"
        else:
            display_text.stylize(
                "reverse",
                start=index,
                end=index + 1,
            )
        return display_text

    def on_focus(self, event: events.Focus) -> None:
        self.refresh(layout=True)

    def on_key(self, event: events.Key) -> None:
        key = event.key
        if key not in self.ALLOW_PROPAGATE:
            event.stop()

        if key == "enter" and self.current_text:
            self.post_message_no_wait(TextInput.Submitted(self, self.current_text))

    class Changed(Message, bubble=True):
        def __init__(self, sender: MessageTarget, value: str) -> None:
            """Message posted when the user changes the value in a TextInput

            Args:
                sender (MessageTarget): Sender of the message
                value (str): The value in the TextInput
            """
            super().__init__(sender)
            self.value = value

    class Submitted(Message, bubble=True):
        def __init__(self, sender: MessageTarget, value: str) -> None:
            """Message posted when the user presses the 'enter' key while
            focused on a TextInput widget.

            Args:
                sender (MessageTarget): Sender of the message
                value (str): The value in the TextInput
            """
            super().__init__(sender)
            self.value = value
