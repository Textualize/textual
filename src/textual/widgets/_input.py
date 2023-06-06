from __future__ import annotations

import re
from dataclasses import dataclass
from typing import ClassVar, Iterable

from rich.cells import cell_len, get_character_cell_size
from rich.console import Console, ConsoleOptions, RenderableType, RenderResult
from rich.highlighter import Highlighter
from rich.segment import Segment
from rich.text import Text

from .. import events
from .._segment_tools import line_crop
from ..binding import Binding, BindingType
from ..events import Blur, Focus, Mount
from ..geometry import Size
from ..message import Message
from ..reactive import reactive
from ..suggester import Suggester, SuggestionReady
from ..validation import ValidationResult, Validator
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
        width = input.content_size.width

        # Add the completion with a faded style.
        value = input.value
        value_length = len(value)
        suggestion = input._suggestion
        show_suggestion = len(suggestion) > value_length
        if show_suggestion:
            result += Text(
                suggestion[value_length:],
                input.get_component_rich_style("input--suggestion"),
            )

        if self.cursor_visible and input.has_focus:
            if not show_suggestion and input._cursor_at_end:
                result.pad_right(1)
            cursor_style = input.get_component_rich_style("input--cursor")
            cursor = input.cursor_position
            result.stylize(cursor_style, cursor, cursor + 1)

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
    | right | Move the cursor right or accept the completion suggestion. |
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

    COMPONENT_CLASSES: ClassVar[set[str]] = {
        "input--cursor",
        "input--placeholder",
        "input--suggestion",
    }
    """
    | Class | Description |
    | :- | :- |
    | `input--cursor` | Target the cursor. |
    | `input--placeholder` | Target the placeholder text (when it exists). |
    | `input--suggestion` | Target the auto-completion suggestion (when it exists). |
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
    Input>.input--placeholder, Input>.input--suggestion {
        color: $text-disabled;
    }
    Input.-invalid {
        border: tall $error 60%;
    }
    Input.-invalid:focus {
        border: tall $error;
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
    suggester: Suggester | None
    """The suggester used to provide completions as the user types."""
    _suggestion = reactive("")
    """A completion suggestion for the current value in the input."""

    @dataclass
    class Changed(Message):
        """Posted when the value changes.

        Can be handled using `on_input_changed` in a subclass of `Input` or in a parent
        widget in the DOM.
        """

        input: Input
        """The `Input` widget that was changed."""

        value: str
        """The value that the input was changed to."""

        validation_result: ValidationResult | None = None
        """The result of validating the value (formed by combining the results from each validator), or None
            if validation was not performed (for example when no validators are specified in the `Input`s init)"""

        @property
        def control(self) -> Input:
            """Alias for self.input."""
            return self.input

    @dataclass
    class Submitted(Message):
        """Posted when the enter key is pressed within an `Input`.

        Can be handled using `on_input_submitted` in a subclass of `Input` or in a
        parent widget in the DOM.
        """

        input: Input
        """The `Input` widget that is being submitted."""
        value: str
        """The value of the `Input` being submitted."""
        validation_result: ValidationResult | None = None
        """The result of validating the value on submission, formed by combining the results for each validator.
        This value will be None if no validation was performed, which will be the case if no validators are supplied
        to the corresponding `Input` widget."""

        @property
        def control(self) -> Input:
            """Alias for self.input."""
            return self.input

    def __init__(
        self,
        value: str | None = None,
        placeholder: str = "",
        highlighter: Highlighter | None = None,
        password: bool = False,
        *,
        suggester: Suggester | None = None,
        validators: Validator | Iterable[Validator] | None = None,
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
            password: Flag to say if the field should obfuscate its content.
            suggester: [`Suggester`][textual.suggester.Suggester] associated with this
                input instance.
            validators: An iterable of validators that the Input value will be checked against.
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
        self.suggester = suggester
        # Ensure we always end up with an Iterable of validators
        if isinstance(validators, Validator):
            self.validators: list[Validator] = [validators]
        elif validators is None:
            self.validators = []
        else:
            self.validators = list(validators) or []

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

    def _watch_cursor_position(self) -> None:
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

    async def _watch_value(self, value: str) -> None:
        self._suggestion = ""
        if self.suggester and value:
            self.run_worker(self.suggester._get_suggestion(self, value))
        if self.styles.auto_dimensions:
            self.refresh(layout=True)

        validation_result = self.validate(value)

        self.post_message(self.Changed(self, value, validation_result))

    def validate(self, value: str) -> ValidationResult | None:
        """Run all the validators associated with this Input on the supplied value.

        Runs all validators, combines the result into one. If any of the validators
        failed, the combined result will be a failure. If no validators are present,
        None will be returned. This also sets the `-invalid` CSS class on the Input
        if the validation fails, and sets the `-valid` CSS class on the Input if
        the validation succeeds.

        Returns:
            A ValidationResult indicating whether *all* validators succeeded or not.
                That is, if *any* validator fails, the result will be an unsuccessful
                validation.
        """
        # If no validators are supplied, and therefore no validation occurs, we return None.
        if not self.validators:
            return None

        validation_results: list[ValidationResult] = [
            validator.validate(value) for validator in self.validators
        ]
        combined_result = ValidationResult.merge(validation_results)
        self.set_class(not combined_result.is_valid, "-invalid")
        self.set_class(combined_result.is_valid, "-valid")
        return combined_result

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

    def _on_mount(self, _: Mount) -> None:
        self.blink_timer = self.set_interval(
            0.5,
            self._toggle_cursor,
            pause=not (self.cursor_blink and self.has_focus),
        )

    def _on_blur(self, _: Blur) -> None:
        self.blink_timer.pause()

    def _on_focus(self, _: Focus) -> None:
        self.cursor_position = len(self.value)
        if self.cursor_blink:
            self.blink_timer.resume()

    async def _on_key(self, event: events.Key) -> None:
        self._cursor_visible = True
        if self.cursor_blink:
            self.blink_timer.reset()

        if event.is_printable:
            event.stop()
            assert event.character is not None
            self.insert_text_at_cursor(event.character)
            event.prevent_default()

    def _on_paste(self, event: events.Paste) -> None:
        if event.text:
            line = event.text.splitlines()[0]
            self.insert_text_at_cursor(line)
        event.stop()

    async def _on_click(self, event: events.Click) -> None:
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

    async def _on_suggestion_ready(self, event: SuggestionReady) -> None:
        """Handle suggestion messages and set the suggestion when relevant."""
        if event.value == self.value:
            self._suggestion = event.suggestion

    def insert_text_at_cursor(self, text: str) -> None:
        """Insert new text at the cursor, move the cursor to the end of the new text.

        Args:
            text: New text to insert.
        """
        if self.cursor_position >= len(self.value):
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
        """Accept an auto-completion or move the cursor one position to the right."""
        if self._cursor_at_end and self._suggestion:
            self.value = self._suggestion
            self.cursor_position = len(self.value)
        else:
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
                    f"{self.value[: self.cursor_position]}{after[hit.end() - 1:]}"
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
        """Handle a submit action.

        Normally triggered by the user pressing Enter. This will also run any validators.
        """
        validation_result = self.validate(self.value)
        self.post_message(self.Submitted(self, self.value, validation_result))
