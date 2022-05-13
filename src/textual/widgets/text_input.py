from __future__ import annotations

from dataclasses import dataclass

from rich.console import RenderableType
from rich.padding import Padding
from rich.text import Text

from textual import events
from textual._types import MessageTarget
from textual.app import ComposeResult
from textual.geometry import Size
from textual.keys import Keys
from textual.message import Message
from textual.widget import Widget


@dataclass
class TextEditorBackend:
    content: str = ""
    cursor_index: int = 0

    def delete_back(self) -> bool:
        """Delete the character behind the cursor

        Returns: True if the text content was modified. False otherwise.
        """
        if self.cursor_index == 0:
            return False

        new_text = (
            self.content[: self.cursor_index - 1] + self.content[self.cursor_index :]
        )
        self.content = new_text
        self.cursor_index = max(0, self.cursor_index - 1)
        return True

    def delete_forward(self) -> bool:
        """Delete the character in front of the cursor

        Returns: True if the text content was modified. False otherwise.
        """
        if self.cursor_index == len(self.content):
            return False

        new_text = (
            self.content[: self.cursor_index] + self.content[self.cursor_index + 1 :]
        )
        self.content = new_text
        return True

    def cursor_left(self) -> bool:
        """Move the cursor 1 character left in the text"""
        previous_index = self.cursor_index
        new_index = max(0, previous_index - 1)
        self.cursor_index = new_index
        return previous_index != new_index

    def cursor_right(self) -> bool:
        """Move the cursor 1 character right in the text"""
        previous_index = self.cursor_index
        new_index = min(len(self.content), previous_index + 1)
        self.cursor_index = new_index
        return previous_index != new_index

    def cursor_text_start(self) -> bool:
        if self.cursor_index == 0:
            return False

        self.cursor_index = 0
        return True

    def cursor_text_end(self) -> bool:
        text_length = len(self.content)
        if self.cursor_index == text_length:
            return False

        self.cursor_index = text_length
        return True

    def insert_at_cursor(self, text: str) -> bool:
        new_text = (
            self.content[: self.cursor_index] + text + self.content[self.cursor_index :]
        )
        self.content = new_text
        self.cursor_index = min(len(self.content), self.cursor_index + 1)
        return True


class TextWidgetBase(Widget):
    STOP_PROPAGATE = set()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text = TextEditorBackend()

    def on_key(self, event: events.Key) -> None:
        key = event.key
        if key == "\x1b":
            return

        changed = False
        if key == "ctrl+h":
            changed = self.text.delete_back()
        elif key == "ctrl+d":
            changed = self.text.delete_forward()
        elif key == "left":
            self.text.cursor_left()
        elif key == "right":
            self.text.cursor_right()
        elif key == "home":
            self.text.cursor_text_start()
        elif key == "end":
            self.text.cursor_text_end()
        elif key not in Keys.values():
            changed = self.text.insert_at_cursor(key)

        if changed:
            self.post_message_no_wait(self.Changed(self, value=self.text.content))

        self.refresh(layout=True)

    def _apply_cursor_to_text(self, display_text: Text, index: int):
        # Either write a cursor character or apply reverse style to cursor location
        at_end_of_text = index == len(display_text)
        at_end_of_line = index < len(display_text) and display_text[index].plain == "\n"
        if at_end_of_text or at_end_of_line:
            display_text = Text.assemble(
                display_text[:index],
                "█",
                display_text[index:],
            )
        else:
            display_text.stylize(
                "reverse",
                start=index,
                end=index + 1,
            )
        return display_text

    class Changed(Message, bubble=True):
        def __init__(self, sender: MessageTarget, value: str) -> None:
            """Message posted when the user changes the value in a TextInput

            Args:
                sender (MessageTarget): Sender of the message
                value (str): The value in the TextInput
            """
            super().__init__(sender)
            self.value = value


class TextInput(Widget):
    CSS = """
        TextInput {
            overflow: hidden hidden;
            background: $primary-darken-1;
            scrollbar-color: $primary-darken-2;
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
        self.initial = initial

    def compose(self) -> ComposeResult:
        yield TextInputChild(
            placeholder=self.placeholder, initial=self.initial, wrapper=self
        )

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


class TextInputChild(TextWidgetBase, can_focus=True):
    CSS = """
    TextInputChild {
        width: auto;
        background: $primary;
        height: 3;
        padding: 0 1;
        content-align: left middle;
        background: $primary-darken-1;
    }

    TextInputChild:hover {
        background: $primary-darken-1;
    }

    TextInputChild:focus {
        background: $primary-darken-2;
        border: hkey $primary-lighten-1;
        padding: 0;
    }

    App.-show-focus TextInputChild:focus {
        tint: $accent 20%;
    }
    """

    def __init__(
        self,
        *,
        wrapper: Widget,
        placeholder: str = "",
        initial: str = "",
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ):
        super().__init__(name=name, id=id, classes=classes)
        self.placeholder = placeholder
        self.text = TextEditorBackend(initial, 0)
        self.wrapper = wrapper

    def get_content_width(self, container_size: Size, viewport_size: Size) -> int:
        return (
            max(len(self.text.content), len(self.placeholder))
            + self.styles.gutter.width
        )

    def render(self) -> RenderableType:
        # We only show the cursor if the widget has focus
        show_cursor = self.has_focus
        if self.text.content:
            display_text = Text(self.text.content, no_wrap=True)

            if show_cursor:
                display_text = self._apply_cursor_to_text(
                    display_text, self.text.cursor_index
                )
            return display_text
        else:
            # The user has not entered text - show the placeholder
            display_text = Text(self.placeholder, "dim")
            if show_cursor:
                display_text = self._apply_cursor_to_text(display_text, 0)
            return display_text

    def on_key(self, event: events.Key) -> None:
        key = event.key
        if key in self.STOP_PROPAGATE:
            event.stop()

        if key == "enter" and self.text.content:
            self.post_message_no_wait(TextInput.Submitted(self, self.text.content))
        elif key == "ctrl+h":
            self.wrapper.scroll_left()
        elif key == "home":
            self.wrapper.scroll_home()
        elif key == "end":
            self.wrapper.scroll_to(x=self.wrapper.max_scroll_x)
        elif key not in Keys.values():
            self.wrapper.scroll_to(x=self.wrapper.scroll_x + 1)


class TextArea(Widget):
    CSS = """
    TextArea { overflow: auto auto; height: 5; background: $primary-darken-1; }
"""

    def compose(self) -> ComposeResult:
        yield TextAreaChild()


class TextAreaChild(TextWidgetBase, can_focus=True):
    # TODO: Not nearly ready for prime-time, but it exists to help
    #  model the superclass.
    CSS = "TextAreaChild { height: auto; background: $primary-darken-1; }"
    STOP_PROPAGATE = {"tab", "shift+tab"}

    def render(self) -> RenderableType:
        # We only show the cursor if the widget has focus
        show_cursor = self.has_focus
        display_text = Text(self.text.content, no_wrap=True)
        if show_cursor:
            display_text = self._apply_cursor_to_text(
                display_text, self.text.cursor_index
            )
        return Padding(display_text, pad=1)

    def get_content_height(
        self, container_size: Size, viewport_size: Size, width: int
    ) -> int:
        return self.text.content.count("\n") + 1 + 2

    def on_key(self, event: events.Key) -> None:
        if event.key in self.STOP_PROPAGATE:
            event.stop()

        if event.key == "enter":
            self.text.insert_at_cursor("\n")
        elif event.key == "tab":
            self.text.insert_at_cursor("\t")
        elif event.key == "\x1b":
            self.app.focused = None

    def on_focus(self, event: events.Focus) -> None:
        self.refresh(layout=True)
