from __future__ import annotations

from typing import Callable

from rich.cells import cell_len
from rich.console import RenderableType
from rich.padding import Padding
from rich.text import Text

from textual import events, _clock
from textual._text_backend import TextEditorBackend
from textual.timer import Timer
from textual._types import MessageTarget
from textual.app import ComposeResult
from textual.geometry import Size, clamp
from textual.message import Message
from textual.reactive import Reactive
from textual.widget import Widget


class TextWidgetBase(Widget):
    """Base class for Widgets which support text input"""

    STOP_PROPAGATE: set[str] = set()
    """Set of keybinds which will not be propagated to parent widgets"""

    cursor_blink_enabled = Reactive(False)
    cursor_blink_period = Reactive(0.6)

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
        if key == "escape":
            return
        changed = False
        if event.char is not None and event.is_printable:
            changed = self._editor.insert(event.char)
        elif key == "ctrl+h":
            changed = self._editor.delete_back()
        elif key == "ctrl+d":
            changed = self._editor.delete_forward()
        elif key == "left":
            self._editor.cursor_left()
        elif key == "right":
            self._editor.cursor_right()
        elif key == "home" or key == "ctrl+a":
            self._editor.cursor_text_start()
        elif key == "end" or key == "ctrl+e":
            self._editor.cursor_text_end()

        self.refresh(layout=True)

        if changed:
            self.post_message_no_wait(self.Changed(self, value=self._editor.content))

    def _apply_cursor_to_text(self, display_text: Text, index: int) -> Text:
        if index < 0:
            return display_text

        # Either write a cursor character or apply reverse style to cursor location
        at_end_of_text = index == len(display_text)
        at_end_of_line = index < len(display_text) and display_text.plain[index] == "\n"

        if at_end_of_text or at_end_of_line:
            display_text = Text.assemble(
                display_text[:index],
                "█",
                display_text[index:],
                overflow="ignore",
                no_wrap=True,
            )
        else:
            display_text.stylize(
                "reverse",
                start=index,
                end=index + 1,
            )
        return display_text

    class Changed(Message, bubble=True):
        namespace = "text_input"

        def __init__(self, sender: MessageTarget, value: str) -> None:
            """Message posted when the user changes the value in a TextInput

            Args:
                sender (MessageTarget): Sender of the message
                value (str): The value in the TextInput
            """
            super().__init__(sender)
            self.value = value


class TextInput(TextWidgetBase, can_focus=True):
    """Widget for inputting text

    Args:
        placeholder (str): The text that will be displayed when there's no content in the TextInput.
            Defaults to an empty string.
        initial (str): The initial value. Defaults to an empty string.
        autocompleter (Callable[[str], str | None): Function which returns autocomplete suggestion
            which will be displayed within the widget any time the content changes. The autocomplete
            suggestion will be displayed as dim text similar to suggestion text in the zsh or fish shells.
    """

    DEFAULT_CSS = """
    TextInput {
        width: auto;
        height: 3;
        padding: 1;
        background: $surface;
        content-align: left middle;
        color: $text;
    }
    TextInput .text-input--placeholder {
        color: $text-muted;
    }
    """

    COMPONENT_CLASSES = {
        "text-input--placeholder",
    }

    def __init__(
        self,
        *,
        placeholder: str = "",
        initial: str = "",
        autocompleter: Callable[[str], str | None] | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ):
        super().__init__(name=name, id=id, classes=classes)
        self.placeholder = placeholder
        self._editor = TextEditorBackend(initial, 0)
        self.visible_range: tuple[int, int] = (0, 0)
        self.autocompleter = autocompleter
        self._suggestion_suffix = ""

        self._cursor_blink_visible = True
        self._cursor_blink_timer: Timer | None = None
        self._last_keypress_time: float = 0.0
        if self.cursor_blink_enabled:
            self._last_keypress_time = _clock.get_time_no_wait()
            self._cursor_blink_timer = self.set_interval(
                self.cursor_blink_period, self._toggle_cursor_visible
            )

    @property
    def value(self) -> str:
        """Get the value from the text input widget as a string

        Returns:
            str: The value in the text input widget
        """
        return self._editor.content

    @value.setter
    def value(self, value: str) -> None:
        """Update the value in the text input widget and move the cursor to the end of
        the new value."""
        self._editor.set_content(value)
        self._editor.cursor_text_end()
        self.refresh()

    def get_content_width(self, container: Size, viewport: Size) -> int:
        # TODO: Why does this need +2 ?
        return min(cell_len(self._editor.content) + 2, container.width)

    def _on_resize(self, event: events.Resize) -> None:
        # Ensure the cursor remains visible when the widget is resized
        self._reset_visible_range()

    async def _on_click(self, event: events.Click) -> None:
        """When the user clicks on the text input, the cursor moves to the
        character that was clicked on. Double-width characters makes this more
        difficult."""

        # If they've clicked outwith the content region (e.g. on padding), do nothing.
        if not self.content_region.contains_point((event.screen_x, event.screen_y)):
            return

        self._cursor_blink_visible = True
        start_index, end_index = self.visible_range

        click_x = event.screen_x - self.content_region.x
        new_cursor_index = start_index + click_x

        # Convert click offset to cursor index accounting for varying cell lengths
        cell_len_accumulated = 0
        for index, character in enumerate(
            self._editor.get_range(start_index, end_index)
        ):
            cell_len_accumulated += cell_len(character)
            if cell_len_accumulated > click_x:
                new_cursor_index = start_index + index
                break

        new_cursor_index = clamp(new_cursor_index, 0, len(self._editor.content))
        self._editor.cursor_index = new_cursor_index
        self.refresh()

    def _on_paste(self, event: events.Paste) -> None:
        """Handle Paste event by stripping newlines from the text, and inserting
        the text at the cursor position, sliding the visible window if required."""
        text = "".join(event.text.splitlines())
        width_behind_cursor = self._visible_content_to_cursor_cell_len
        self._editor.insert(text)
        paste_cell_len = cell_len(text)
        available_width = self.content_region.width

        # By inserting the pasted text, how far beyond the bounds of the text input
        # will we move the cursor? We need to slide the visible window along by that.
        scroll_amount = paste_cell_len + width_behind_cursor - available_width + 1

        if scroll_amount > 0:
            self._slide_window(scroll_amount)

        self.refresh()

    def _slide_window(self, amount: int) -> None:
        """Slide the visible window left or right by `amount`. Negative integers move
        the window left, and positive integers move the window right."""
        start, end = self.visible_range
        self.visible_range = start + amount, end + amount

    def _reset_visible_range(self):
        """Reset our window into the editor content. Used when the widget is resized."""
        available_width = self.content_region.width

        # Adjust the window end such that the cursor is just off of it
        new_visible_range_end = max(self._editor.cursor_index + 2, available_width)
        # The visible window extends back by the width of the content region
        new_visible_range_start = new_visible_range_end - available_width

        # Check the cell length of the newly visible content and adjust window to accommodate
        new_range = self._editor.get_range(
            new_visible_range_start, new_visible_range_end
        )
        new_range_cell_len = cell_len(new_range)
        additional_shift_required = max(0, new_range_cell_len - available_width)

        self.visible_range = (
            new_visible_range_start + additional_shift_required,
            new_visible_range_end + additional_shift_required,
        )

        self.refresh()

    def render(self) -> RenderableType:
        # First render: Cursor at start of text, visible range goes from cursor to content region width
        if not self.visible_range:
            self.visible_range = (self._editor.cursor_index, self.content_region.width)

        # We only show the cursor if the widget has focus
        show_cursor = self.has_focus and self._cursor_blink_visible
        if self._editor.content:
            start, end = self.visible_range
            visible_text = self._editor.get_range(start, end)
            display_text = Text(visible_text, no_wrap=True, overflow="ignore")

            if self._suggestion_suffix:
                display_text.append(self._suggestion_suffix, "dim")

            if show_cursor:
                display_text = self._apply_cursor_to_text(
                    display_text, self._editor.cursor_index - start
                )
            return display_text
        else:
            # The user has not entered text - show the placeholder
            display_text = Text(
                self.placeholder,
                self.get_component_rich_style("text-input--placeholder"),
                no_wrap=True,
                overflow="ignore",
            )
            if show_cursor:
                display_text = self._apply_cursor_to_text(display_text, 0)
            return display_text

    @property
    def _visible_content_to_cursor_cell_len(self) -> int:
        """The cell width of the visible content up to the cursor cell"""
        start, _ = self.visible_range
        visible_content_to_cursor = self._editor.get_range(
            start, self._editor.cursor_index + 1
        )
        return cell_len(visible_content_to_cursor)

    @property
    def _cursor_at_right_edge(self) -> bool:
        """True if the cursor is at the right edge of the content area"""
        return self._visible_content_to_cursor_cell_len == self.content_region.width

    def _on_key(self, event: events.Key) -> None:
        key = event.key
        if key in self.STOP_PROPAGATE:
            event.stop()

        self._last_keypress_time = _clock.get_time_no_wait()
        if self._cursor_blink_timer:
            self._cursor_blink_visible = True

        # Cursor location and the *codepoint* range of our view into the content
        start, end = self.visible_range
        cursor_index = self._editor.cursor_index

        # We can scroll if the cell width of the content is greater than the content region
        available_width = self.content_region.width
        scrollable = cell_len(self._editor.content) >= available_width

        # Check what content is visible from the editor, and how wide that content is
        visible_content_to_cursor_cell_len = self._visible_content_to_cursor_cell_len

        cursor_at_end = self._cursor_at_right_edge
        key_cell_len = cell_len(key)
        if event.is_printable:
            # Check if we'll need to scroll to accommodate the new cell width after insertion.
            if visible_content_to_cursor_cell_len + key_cell_len >= available_width:
                self._slide_window(key_cell_len)
            self._update_suggestion(event)
        elif key == "enter" and self._editor.content:
            self.post_message_no_wait(TextInput.Submitted(self, self._editor.content))
        elif key == "right":
            if (
                cursor_at_end
                or visible_content_to_cursor_cell_len == available_width - 1
                and cell_len(self._editor.query_cursor_right() or "") == 2
            ):
                if scrollable:
                    character_to_right = self._editor.query_cursor_right()
                    if character_to_right is not None:
                        cell_width_character_to_right = cell_len(character_to_right)
                        window_shift_amount = cell_width_character_to_right
                    else:
                        window_shift_amount = 1
                    self._slide_window(window_shift_amount)
            if self._suggestion_suffix and self._editor.cursor_at_end:
                self._editor.insert(self._suggestion_suffix)
                self._suggestion_suffix = ""
                self._reset_visible_range()
        elif key == "left":
            if cursor_index == start:
                if scrollable and self._editor.query_cursor_left():
                    self.visible_range = (
                        cursor_index - 1,
                        cursor_index + available_width - 1,
                    )
                else:
                    self.app.bell()
        elif key == "ctrl+h":
            if cursor_index == start and self._editor.query_cursor_left():
                self._slide_window(-1)
            self._update_suggestion(event)
        elif key == "ctrl+d":
            self._update_suggestion(event)
        elif key == "home" or key == "ctrl+a":
            self.visible_range = (0, available_width)
        elif key == "end" or key == "ctrl+e":
            num_codepoints = len(self.value)
            final_visible_codepoints = self._editor.get_range(
                num_codepoints - available_width + 1,
                max(num_codepoints, available_width) + 1,
            )
            cell_len_final_visible = cell_len(final_visible_codepoints)

            # Additional shift to ensure there's space for double width character
            additional_shift_required = (
                max(0, cell_len_final_visible - available_width) + 2
            )
            if scrollable:
                self.visible_range = (
                    num_codepoints - available_width + additional_shift_required,
                    max(available_width, num_codepoints) + additional_shift_required,
                )
            else:
                self.visible_range = (0, available_width)

        # We need to clamp the visible range to ensure we don't use negative indexing
        start, end = self.visible_range
        self.visible_range = (max(0, start), end)

    def _update_suggestion(self, event: events.Key) -> None:
        """Run the autocompleter function, updating the suggestion if necessary"""
        if self.autocompleter is not None:
            # TODO: We shouldn't be doing the stuff below here, maybe we need to add
            #  a method to the editor to query an edit operation?
            event.prevent_default()
            super().on_key(event)
            if self.value:
                full_suggestion = self.autocompleter(self.value)
                if full_suggestion:
                    suffix = full_suggestion[len(self.value) :]
                    self._suggestion_suffix = suffix
                else:
                    self._suggestion_suffix = None
            else:
                self._suggestion_suffix = None

    def _toggle_cursor_visible(self):
        """Manages the blinking of the cursor - ensuring blinking only starts when the
        user hasn't pressed a key in some time"""
        if (
            _clock.get_time_no_wait() - self._last_keypress_time
            > self.cursor_blink_period
        ):
            self._cursor_blink_visible = not self._cursor_blink_visible
            self.refresh()

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
    DEFAULT_CSS = """
    TextArea { overflow: auto auto; height: 5; background: $primary-darken-1; }
"""

    def compose(self) -> ComposeResult:
        yield TextAreaChild()


class TextAreaChild(TextWidgetBase, can_focus=True):
    # TODO: Not nearly ready for prime-time, but it exists to help
    #  model the superclass.
    DEFAULT_CSS = "TextAreaChild { height: auto; background: $primary-darken-1; }"
    STOP_PROPAGATE = {"tab", "shift+tab"}

    def render(self) -> RenderableType:
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

    def _on_key(self, event: events.Key) -> None:
        if event.key in self.STOP_PROPAGATE:
            event.stop()

        if event.key == "enter":
            self._editor.insert("\n")
        elif event.key == "tab":
            self._editor.insert("\t")
        elif event.key == "escape":
            self.app.focused = None

    def _on_focus(self, event: events.Focus) -> None:
        self.refresh(layout=True)
