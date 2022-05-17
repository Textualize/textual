from __future__ import annotations

from rich.console import RenderableType
from rich.padding import Padding
from rich.style import Style
from rich.text import Text

from textual import events
from textual._text_backend import TextEditorBackend
from textual._types import MessageTarget
from textual.app import ComposeResult
from textual.geometry import Size
from textual.keys import Keys
from textual.message import Message
from textual.widget import Widget


class TextWidgetBase(Widget):
    STOP_PROPAGATE = set()

    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ):
        super().__init__(name=name, id=id, classes=classes)
        self._editor = TextEditorBackend()

    def on_key(self, event: events.Key) -> None:
        key = event.key
        if key == "\x1b":
            return

        changed = False
        if key == "ctrl+h":
            changed = self._editor.delete_back()
        elif key == "ctrl+d":
            changed = self._editor.delete_forward()
        elif key == "left":
            self._editor.cursor_left()
        elif key == "right":
            self._editor.cursor_right()
        elif key == "home":
            self._editor.cursor_text_start()
        elif key == "end":
            self._editor.cursor_text_end()
        elif key not in Keys.values():
            changed = self._editor.insert_at_cursor(key)

        if changed:
            self.post_message_no_wait(self.Changed(self, value=self._editor.content))

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


class TextInput(TextWidgetBase, can_focus=True):
    CSS = """
    TextInput {
        width: auto;
        background: $primary;
        height: 3;
        padding: 0 1;
        content-align: left middle;
        background: $primary-darken-1;
    }

    TextInput:hover {
        background: $primary-darken-2;
    }

    TextInput:focus {
        background: $primary-darken-2;
        border: heavy $primary-lighten-1;
        padding: 0;
    }

    App.-show-focus TextInput:focus {
        tint: $accent 20%;
    }
    """

    def __init__(
        self,
        *,
        placeholder: str = "",
        initial: str = "",
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ):
        super().__init__(name=name, id=id, classes=classes)
        self.placeholder = placeholder
        self._editor = TextEditorBackend(initial, 0)
        self.visible_range: tuple[int, int] | None = None

    @property
    def value(self):
        return self._editor.content

    @value.setter
    def value(self, value: str):
        self._editor.set_content(value)
        self._editor.cursor_text_end()
        self.refresh(layout=True)

    def render(self, style: Style) -> RenderableType:
        # First render: Cursor at start of text, visible range goes from cursor to content region width
        if not self.visible_range:
            self.visible_range = (self._editor.cursor_index, self.content_region.width)

        # We only show the cursor if the widget has focus
        show_cursor = self.has_focus
        if self._editor.content:
            start, end = self.visible_range
            visible_text = self._editor.get_range(start, end)
            display_text = Text(visible_text, no_wrap=True)

            if show_cursor:
                display_text = self._apply_cursor_to_text(
                    display_text, self._editor.cursor_index - start
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

        start, end = self.visible_range
        cursor_index = self._editor.cursor_index
        available_width = self.content_region.width
        scrollable = len(self._editor.content) >= available_width
        if key == "enter" and self._editor.content:
            self.post_message_no_wait(TextInput.Submitted(self, self._editor.content))
        elif key == "right":
            if cursor_index == end - 1:
                if scrollable and self._editor.query_cursor_right():
                    self.visible_range = (start + 1, end + 1)
                else:
                    self.app.bell()
        elif key == "left":
            if cursor_index == start:
                if scrollable and self._editor.query_cursor_left():
                    self.visible_range = (
                        cursor_index - 1,
                        cursor_index + available_width - 1,
                    )
                else:
                    # If the user has hit the scroll limit
                    self.app.bell()
        elif key == "ctrl+h":
            if cursor_index == start and self._editor.query_cursor_left():
                self.visible_range = start - 1, end - 1
        elif key == "home":
            self.visible_range = (0, available_width)
        elif key == "end":
            value_length = len(self.value)
            if scrollable:
                self.visible_range = (
                    value_length - available_width + 1,
                    max(available_width, value_length) + 1,
                )
            else:
                self.visible_range = (0, available_width)
        elif key not in Keys.values():
            # If we're at the end of the visible range, and the editor backend
            # will permit us to move the cursor right, then shift the visible
            # window/range along to the right.
            if cursor_index == end - 1:
                self.visible_range = start + 1, end + 1

        # We need to clamp the visible range to ensure we don't use negative indexing
        start, end = self.visible_range
        self.visible_range = (max(0, start), end)

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

    def render(self, style: Style) -> RenderableType:
        # We only show the cursor if the widget has focus
        show_cursor = self.has_focus
        display_text = Text(self._editor.content, no_wrap=True)
        if show_cursor:
            display_text = self._apply_cursor_to_text(
                display_text, self._editor.cursor_index
            )
        return Padding(display_text, pad=1)

    def get_content_height(
        self, container_size: Size, viewport_size: Size, width: int
    ) -> int:
        return self._editor.content.count("\n") + 1 + 2

    def on_key(self, event: events.Key) -> None:
        if event.key in self.STOP_PROPAGATE:
            event.stop()

        if event.key == "enter":
            self._editor.insert_at_cursor("\n")
        elif event.key == "tab":
            self._editor.insert_at_cursor("\t")
        elif event.key == "\x1b":
            self.app.focused = None

    def on_focus(self, event: events.Focus) -> None:
        self.refresh(layout=True)
