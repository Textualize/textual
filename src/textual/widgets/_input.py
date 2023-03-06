from __future__ import annotations

import re
from typing import ClassVar

from rich.cells import cell_len, get_character_cell_size
from rich.console import Console, ConsoleOptions, RenderableType, RenderResult
from rich.highlighter import Highlighter
from rich.segment import Segment
from rich.text import Text

from .. import events
from .._segment_tools import line_crop
from ..binding import Binding, BindingType
from ..geometry import Size
from ..message import Message
from ..reactive import reactive
from ..widget import Widget


class _InputRenderable:
    """Render the input content."""

    def __init__(self, input: Input, cursor_visible: bool) -> None:
        self.input = input
        self.cursor_visible = cursor_visible

    def __rich_console__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> "RenderResult":
        input = self.input
        result = input._value
        if input._cursor_at_end:
            result.pad_right(1)
        cursor_style = input.get_component_rich_style("input--cursor")
        if self.cursor_visible and input.has_focus:
            cursor = input.cursor_position
            result.stylize(cursor_style, cursor, cursor + 1)
        width = input.content_size.width
        segments = list(result.render(console))
        line_length = Segment.get_line_length(segments)
        if line_length < width:
            segments = Segment.adjust_line_length(segments, width)
            line_length = width

        line = line_crop(
            list(segments),
            input.view_position,
            input.view_position + width,
            line_length,
        )
        yield from line


class Input(Widget, can_focus=True):
    """A text input widget."""

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("left", "cursor_left", "cursor left", show=False),
        Binding("ctrl+left", "cursor_left_word", "cursor left word", show=False),
        Binding("right", "cursor_right", "cursor right", show=False),
        Binding("ctrl+right", "cursor_right_word", "cursor right word", show=False),
        Binding("backspace", "delete_left", "delete left", show=False),
        Binding("home,ctrl+a", "home", "home", show=False),
        Binding("end,ctrl+e", "end", "end", show=False),
        Binding("delete,ctrl+d", "delete_right", "delete right", show=False),
        Binding("enter", "submit", "submit", show=False),
        Binding(
            "ctrl+w", "delete_left_word", "delete left to start of word", show=False
        ),
        Binding("ctrl+u", "delete_left_all", "delete all to the left", show=False),
        Binding(
            "ctrl+f", "delete_right_word", "delete right to start of word", show=False
        ),
        Binding("ctrl+k", "delete_right_all", "delete all to the right", show=False),
    ]
    """
    | Key(s) | Description |
    | :- | :- |
    | left | Move the cursor left. |
    | ctrl+left | Move the cursor one word to the left. |
    | right | Move the cursor right. |
    | ctrl+right | Move the cursor one word to the right. |
    | backspace | Delete the character to the left of the cursor. |
    | home,ctrl+a | Go to the beginning of the input. |
    | end,ctrl+e | Go to the end of the input. |
    | delete,ctrl+d | Delete the character to the right of the cursor. |
    | enter | Submit the current value of the input. |
    | ctrl+w | Delete the word to the left of the cursor. |
    | ctrl+u | Delete everything to the left of the cursor. |
    | ctrl+f | Delete the word to the right of the cursor. |
    | ctrl+k | Delete everything to the right of the cursor. |
    """

    COMPONENT_CLASSES: ClassVar[set[str]] = {"input--cursor", "input--placeholder"}
    """
    | Class | Description |
    | :- | :- |
    | `input--cursor` | Target the cursor. |
    | `input--placeholder` | Target the placeholder text (when it exists). |
    """

    DEFAULT_CSS = """
    Input {
        background: $boost;
        color: $text;
        padding: 0 2;
        border: tall $background;
        width: 100%;
        height: 1;
        min-height: 1;
    }
    Input:focus {
        border: tall $accent;
    }
    Input>.input--cursor {
        background: $surface;
        color: $text;
        text-style: reverse;
    }
    Input>.input--placeholder {
        color: $text-disabled;
    }
    """

    cursor_blink = reactive(True)
    value = reactive("", layout=True, init=False)
    input_scroll_offset = reactive(0)
    cursor_position = reactive(0)
    view_position = reactive(0)
    placeholder = reactive("")
    complete = reactive("")
    width = reactive(1)
    _cursor_visible = reactive(True)
    password = reactive(False)
    max_size: reactive[int | None] = reactive(None)

    class Changed(Message, bubble=True):
        """Posted when the value changes.

        Can be handled using `on_input_changed` in a subclass of `Input` or in a parent
        widget in the DOM.

        Attributes:
            value: The value that the input was changed to.
            input: The `Input` widget that was changed.
        """

        def __init__(self, sender: Input, value: str) -> None:
            super().__init__(sender)
            self.value: str = value
            self.input: Input = sender

    class Submitted(Message, bubble=True):
        """Posted when the enter key is pressed within an `Input`.

        Can be handled using `on_input_submitted` in a subclass of `Input` or in a
        parent widget in the DOM.

        Attributes:
            value: The value of the `Input` being submitted.
            input: The `Input` widget that is being submitted.
        """

        def __init__(self, sender: Input, value: str) -> None:
            super().__init__(sender)
            self.value: str = value
            self.input: Input = sender

    def __init__(
        self,
        value: str | None = None,
        placeholder: str = "",
        highlighter: Highlighter | None = None,
        password: bool = False,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        """Initialise the `Input` widget.

        Args:
            value: An optional default value for the input.
            placeholder: Optional placeholder text for the input.
            highlighter: An optional highlighter for the input.
            password: Flag to say if the field should obfuscate its content. Default is `False`.
            name: Optional name for the input widget.
            id: Optional ID for the widget.
            classes: Optional initial classes for the widget.
            disabled: Whether the input is disabled or not.
        """
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        if value is not None:
            self.value = value
        self.placeholder = placeholder
        self.highlighter = highlighter
        self.password = password

    def _position_to_cell(self, position: int) -> int:
        """Convert an index within the value to cell position."""
        cell_offset = cell_len(self.value[:position])
        return cell_offset

    @property
    def _cursor_offset(self) -> int:
        """The cell offset of the cursor."""
        offset = self._position_to_cell(self.cursor_position)
        if self._cursor_at_end:
            offset += 1
        return offset

    @property
    def _cursor_at_end(self) -> bool:
        """Flag to indicate if the cursor is at the end"""
        return self.cursor_position >= len(self.value)

    def validate_cursor_position(self, cursor_position: int) -> int:
        return min(max(0, cursor_position), len(self.value))

    def validate_view_position(self, view_position: int) -> int:
        width = self.content_size.width
        new_view_position = max(0, min(view_position, self.cursor_width - width))
        return new_view_position

    def watch_cursor_position(self, cursor_position: int) -> None:
        width = self.content_size.width
        if width == 0:
            # If the input has no width the view position can't be elsewhere.
            self.view_position = 0
            return

        view_start = self.view_position
        view_end = view_start + width
        cursor_offset = self._cursor_offset

        if cursor_offset >= view_end or cursor_offset < view_start:
            view_position = cursor_offset - width // 2
            self.view_position = view_position
        else:
            self.view_position = self.view_position

    async def watch_value(self, value: str) -> None:
        if self.styles.auto_dimensions:
            self.refresh(layout=True)
        await self.post_message(self.Changed(self, value))

    @property
    def cursor_width(self) -> int:
        """The width of the input (with extra space for cursor at the end)."""
        if self.placeholder and not self.value:
            return cell_len(self.placeholder)
        return self._position_to_cell(len(self.value)) + 1

    def render(self) -> RenderableType:
        self.view_position = self.view_position
        if not self.value:
            placeholder = Text(self.placeholder, justify="left")
            placeholder.stylize(self.get_component_rich_style("input--placeholder"))
            if self.has_focus:
                cursor_style = self.get_component_rich_style("input--cursor")
                if self._cursor_visible:
                    # If the placeholder is empty, there's no characters to stylise
                    # to make the cursor flash, so use a single space character
                    if len(placeholder) == 0:
                        placeholder = Text(" ")
                    placeholder.stylize(cursor_style, 0, 1)
            return placeholder
        return _InputRenderable(self, self._cursor_visible)

    @property
    def _value(self) -> Text:
        """Value rendered as text."""
        if self.password:
            return Text("•" * len(self.value), no_wrap=True, overflow="ignore")
        else:
            text = Text(self.value, no_wrap=True, overflow="ignore")
            if self.highlighter is not None:
                text = self.highlighter(text)
            return text

    def get_content_width(self, container: Size, viewport: Size) -> int:
        return self.cursor_width

    def get_content_height(self, container: Size, viewport: Size, width: int) -> int:
        return 1

    def _toggle_cursor(self) -> None:
        """Toggle visibility of cursor."""
        self._cursor_visible = not self._cursor_visible

    def on_mount(self) -> None:
        self.blink_timer = self.set_interval(
            0.5,
            self._toggle_cursor,
            pause=not (self.cursor_blink and self.has_focus),
        )

    def on_blur(self) -> None:
        self.blink_timer.pause()

    def on_focus(self) -> None:
        self.cursor_position = len(self.value)
        if self.cursor_blink:
            self.blink_timer.resume()

    async def on_key(self, event: events.Key) -> None:
        self._cursor_visible = True
        if self.cursor_blink:
            self.blink_timer.reset()

        # Do key bindings first
        if await self.handle_key(event):
            event.prevent_default()
            event.stop()
            return
        elif event.is_printable:
            event.stop()
            assert event.character is not None
            self.insert_text_at_cursor(event.character)
            event.prevent_default()

    def on_paste(self, event: events.Paste) -> None:
        line = event.text.splitlines()[0]
        self.insert_text_at_cursor(line)
        event.stop()

    def on_click(self, event: events.Click) -> None:
        offset = event.get_content_offset(self)
        if offset is None:
            return
        event.stop()
        click_x = offset.x + self.view_position
        cell_offset = 0
        _cell_size = get_character_cell_size
        for index, char in enumerate(self.value):
            if cell_offset >= click_x:
                self.cursor_position = index
                break
            cell_offset += _cell_size(char)
        else:
            self.cursor_position = len(self.value)

    def insert_text_at_cursor(self, text: str) -> None:
        """Insert new text at the cursor, move the cursor to the end of the new text.

        Args:
            text: New text to insert.
        """
        if self.cursor_position > len(self.value):
            self.value += text
            self.cursor_position = len(self.value)
        else:
            value = self.value
            before = value[: self.cursor_position]
            after = value[self.cursor_position :]
            self.value = f"{before}{text}{after}"
            self.cursor_position += len(text)

    def action_cursor_left(self) -> None:
        """Move the cursor one position to the left."""
        self.cursor_position -= 1

    def action_cursor_right(self) -> None:
        """Move the cursor one position to the right."""
        self.cursor_position += 1

    def action_home(self) -> None:
        """Move the cursor to the start of the input."""
        self.cursor_position = 0

    def action_end(self) -> None:
        """Move the cursor to the end of the input."""
        self.cursor_position = len(self.value)

    _WORD_START = re.compile(r"(?<=\W)\w")

    def action_cursor_left_word(self) -> None:
        """Move the cursor left to the start of a word."""
        if self.password:
            # This is a password field so don't give any hints about word
            # boundaries, even during movement.
            self.action_home()
        else:
            try:
                *_, hit = re.finditer(
                    self._WORD_START, self.value[: self.cursor_position]
                )
            except ValueError:
                self.cursor_position = 0
            else:
                self.cursor_position = hit.start()

    def action_cursor_right_word(self) -> None:
        """Move the cursor right to the start of a word."""
        if self.password:
            # This is a password field so don't give any hints about word
            # boundaries, even during movement.
            self.action_end()
        else:
            hit = re.search(self._WORD_START, self.value[self.cursor_position :])
            if hit is None:
                self.cursor_position = len(self.value)
            else:
                self.cursor_position += hit.start()

    def action_delete_right(self) -> None:
        """Delete one character at the current cursor position."""
        value = self.value
        delete_position = self.cursor_position
        before = value[:delete_position]
        after = value[delete_position + 1 :]
        self.value = f"{before}{after}"
        self.cursor_position = delete_position

    def action_delete_right_word(self) -> None:
        """Delete the current character and all rightward to the start of the next word."""
        if self.password:
            # This is a password field so don't give any hints about word
            # boundaries, even during deletion.
            self.action_delete_right_all()
        else:
            after = self.value[self.cursor_position :]
            hit = re.search(self._WORD_START, after)
            if hit is None:
                self.value = self.value[: self.cursor_position]
            else:
                self.value = (
                    f"{self.value[: self.cursor_position]}{after[hit.end()-1 :]}"
                )

    def action_delete_right_all(self) -> None:
        """Delete the current character and all characters to the right of the cursor position."""
        self.value = self.value[: self.cursor_position]

    def action_delete_left(self) -> None:
        """Delete one character to the left of the current cursor position."""
        if self.cursor_position <= 0:
            # Cursor at the start, so nothing to delete
            return
        if self.cursor_position == len(self.value):
            # Delete from end
            self.value = self.value[:-1]
            self.cursor_position = len(self.value)
        else:
            # Cursor in the middle
            value = self.value
            delete_position = self.cursor_position - 1
            before = value[:delete_position]
            after = value[delete_position + 1 :]
            self.value = f"{before}{after}"
            self.cursor_position = delete_position

    def action_delete_left_word(self) -> None:
        """Delete leftward of the cursor position to the start of a word."""
        if self.cursor_position <= 0:
            return
        if self.password:
            # This is a password field so don't give any hints about word
            # boundaries, even during deletion.
            self.action_delete_left_all()
        else:
            after = self.value[self.cursor_position :]
            try:
                *_, hit = re.finditer(
                    self._WORD_START, self.value[: self.cursor_position]
                )
            except ValueError:
                self.cursor_position = 0
            else:
                self.cursor_position = hit.start()
            self.value = f"{self.value[: self.cursor_position]}{after}"

    def action_delete_left_all(self) -> None:
        """Delete all characters to the left of the cursor position."""
        if self.cursor_position > 0:
            self.value = self.value[self.cursor_position :]
            self.cursor_position = 0

    async def action_submit(self) -> None:
        """Handle a submit action (normally the user hitting Enter in the input)."""
        await self.post_message(self.Submitted(self, self.value))
