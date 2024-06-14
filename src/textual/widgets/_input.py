from __future__ import annotations

import re
from dataclasses import dataclass
from enum import IntFlag
from typing import TYPE_CHECKING, ClassVar, Iterable, Pattern

from rich.cells import cell_len, get_character_cell_size
from rich.console import Console, ConsoleOptions, RenderableType
from rich.console import RenderResult as RichRenderResult
from rich.highlighter import Highlighter
from rich.segment import Segment
from rich.text import Text
from typing_extensions import Literal

from .. import events
from .._segment_tools import line_crop

if TYPE_CHECKING:
    from ..app import RenderResult

from ..binding import Binding, BindingType
from ..css._error_tools import friendly_list
from ..events import Blur, Focus, Mount
from ..geometry import Offset, Size
from ..message import Message
from ..reactive import Reactive, reactive, var
from ..suggester import Suggester, SuggestionReady
from ..timer import Timer
from ..validation import ValidationResult, Validator
from ..widget import Widget

InputValidationOn = Literal["blur", "changed", "submitted"]
"""Possible messages that trigger input validation."""
_POSSIBLE_VALIDATE_ON_VALUES = {"blur", "changed", "submitted"}
"""Set literal with the legal values for the type `InputValidationOn`."""


_RESTRICT_TYPES = {
    "integer": r"[-+]?\d*",
    "number": r"[-+]?\d*\.?\d*[eE]?[-+]?\d*",
    "text": None,
}
InputType = Literal["integer", "number", "text"]


class _CharFlags(IntFlag):
    """Misc flags for a single template character definition"""

    REQUIRED = 0x1
    """Is this character required for validation?"""

    SEPARATOR = 0x2
    """Is this character a separator?"""

    UPPERCASE = 0x4
    """Char is forced to be uppercase"""

    LOWERCASE = 0x8
    """Char is forced to be lowercase"""


_TEMPLATE_CHARACTERS = {
    "A": (r"[A-Za-z]", _CharFlags.REQUIRED),
    "a": (r"[A-Za-z]", None),
    "N": (r"[A-Za-z0-9]", _CharFlags.REQUIRED),
    "n": (r"[A-Za-z0-9]", None),
    "X": (r"[^ ]", _CharFlags.REQUIRED),
    "x": (r"[^ ]", None),
    "9": (r"[0-9]", _CharFlags.REQUIRED),
    "0": (r"[0-9]", None),
    "D": (r"[1-9]", _CharFlags.REQUIRED),
    "d": (r"[1-9]", None),
    "#": (r"[0-9+\-]", None),
    "H": (r"[A-Fa-f0-9]", _CharFlags.REQUIRED),
    "h": (r"[A-Fa-f0-9]", None),
    "B": (r"[0-1]", _CharFlags.REQUIRED),
    "b": (r"[0-1]", None),
}


class _InputRenderable:
    """Render the input content."""

    def __init__(self, input: Input, cursor_visible: bool) -> None:
        self.input = input
        self.cursor_visible = cursor_visible

    def __rich_console__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> RichRenderResult:
        input = self.input
        result = input._value
        width = input.content_size.width

        # Add the completion with a faded style.
        value = input.value
        value_length = len(value)
        template = input._template
        suggestion = input._suggestion
        show_suggestion = len(suggestion) > value_length and input.has_focus
        if show_suggestion:
            result += Text(
                suggestion[value_length:],
                input.get_component_rich_style("input--suggestion"),
            )
        elif template is not None:
            style = input.get_component_rich_style("input--placeholder")
            result += Text(
                template.mask[value_length:],
                style,
            )
            for index, (c, char_def) in enumerate(zip(value, template.template)):
                if c == " ":
                    result.stylize(style, index, index + 1)

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


class _Template(Validator):
    """Template mask enforcer."""

    @dataclass
    class CharDef:
        """Holds data for a single char of the template mask."""

        pattern: Pattern[str]
        """Compiled regular expression to check for matches."""

        flags: _CharFlags = _CharFlags(0)
        """Flags defining special behaviors"""

        char: str = ""
        """Mask character (separator or blank or placeholder)"""

    def __init__(self, input: Input, template_str: str) -> None:
        self.input = input
        self.template: list[_Template.CharDef] = []
        self.blank: str = " "
        escaped = False
        flags = _CharFlags(0)
        template_chars: list[str] = list(template_str)

        while template_chars:
            c = template_chars.pop(0)
            if escaped:
                char = self.CharDef(re.compile(re.escape(c)), _CharFlags.SEPARATOR, c)
                escaped = False
            else:
                if c == "\\":
                    escaped = True
                    continue
                elif c == ";":
                    break

                new_flags = {
                    ">": _CharFlags.UPPERCASE,
                    "<": _CharFlags.LOWERCASE,
                    "!": 0,
                }.get(c, None)
                if new_flags is not None:
                    flags = new_flags
                    continue

                pattern, required_flag = _TEMPLATE_CHARACTERS.get(c, (None, None))
                if pattern:
                    char_flags = _CharFlags.REQUIRED if required_flag else _CharFlags(0)
                    char = self.CharDef(re.compile(pattern), char_flags)
                else:
                    char = self.CharDef(
                        re.compile(re.escape(c)), _CharFlags.SEPARATOR, c
                    )

            char.flags |= flags
            self.template.append(char)

        if template_chars:
            self.blank = template_chars[0]

        if all(char.flags & _CharFlags.SEPARATOR for char in self.template):
            raise ValueError(
                "Template must contain at least one non-separator character"
            )

        self.update_mask(input.placeholder)

    def validate(self, value: str) -> ValidationResult:
        if self.check(value.ljust(len(self.template), chr(0)), False):
            return self.success()
        else:
            return self.failure("Value does not match template!", value)

    def check(self, value: str, allow_space: bool) -> bool:
        for c, char_def in zip(value, self.template):
            if (
                (char_def.flags & _CharFlags.REQUIRED)
                and (not char_def.pattern.match(c))
                and ((c != " ") or not allow_space)
            ):
                return False
        return True

    def insert_separators(self, value: str, cursor_position: int) -> tuple[str, int]:
        while cursor_position < len(self.template) and (
            self.template[cursor_position].flags & _CharFlags.SEPARATOR
        ):
            value = (
                value[:cursor_position]
                + self.template[cursor_position].char
                + value[cursor_position + 1 :]
            )
            cursor_position += 1
        return value, cursor_position

    def insert_text_at_cursor(self, text: str) -> str | None:
        value = self.input.value
        cursor_position = self.input.cursor_position
        separators = set(
            [
                char_def.char
                for char_def in self.template
                if char_def.flags & _CharFlags.SEPARATOR
            ]
        )
        for c in text:
            if c in separators:
                if c == self.next_separator(cursor_position):
                    prev_position = self.prev_separator_position(cursor_position)
                    if (cursor_position > 0) and (prev_position != cursor_position - 1):
                        next_position = self.next_separator_position(cursor_position)
                        while cursor_position < next_position + 1:
                            if (
                                self.template[cursor_position].flags
                                & _CharFlags.SEPARATOR
                            ):
                                char = self.template[cursor_position].char
                            else:
                                char = " "
                            value = (
                                value[:cursor_position]
                                + char
                                + value[cursor_position + 1 :]
                            )
                            cursor_position += 1
                continue
            if cursor_position >= len(self.template):
                break
            char_def = self.template[cursor_position]
            assert (char_def.flags & _CharFlags.SEPARATOR) == 0
            if not char_def.pattern.match(c):
                return None
            if char_def.flags & _CharFlags.LOWERCASE:
                c = c.lower()
            elif char_def.flags & _CharFlags.UPPERCASE:
                c = c.upper()
            value = value[:cursor_position] + c + value[cursor_position + 1 :]
            cursor_position += 1
            value, cursor_position = self.insert_separators(value, cursor_position)
        return value, cursor_position

    def move_cursor(self, delta: int) -> None:
        cursor_position = self.input.cursor_position
        if delta < 0 and all(
            [c.flags & _CharFlags.SEPARATOR for c in self.template[:cursor_position]]
        ):
            return
        cursor_position += delta
        while (
            (cursor_position >= 0)
            and (cursor_position < len(self.template))
            and (self.template[cursor_position].flags & _CharFlags.SEPARATOR)
        ):
            cursor_position += delta
        self.input.cursor_position = cursor_position

    def delete_at_position(self, position: int | None = None) -> None:
        value = self.input.value
        if position is None:
            position = self.input.cursor_position
        cursor_position = position
        if cursor_position < len(self.template):
            assert (self.template[cursor_position].flags & _CharFlags.SEPARATOR) == 0
            if cursor_position == len(value) - 1:
                value = value[:cursor_position]
            else:
                value = value[:cursor_position] + " " + value[cursor_position + 1 :]
        pos = len(value)
        while pos > 0:
            char_def = self.template[pos - 1]
            if ((char_def.flags & _CharFlags.SEPARATOR) == 0) and (
                value[pos - 1] != " "
            ):
                break
            pos -= 1
        value = value[:pos]
        if cursor_position > len(value):
            cursor_position = len(value)
        value, cursor_position = self.insert_separators(value, cursor_position)
        self.input.cursor_position = cursor_position
        self.input.value = value

    def at_separator(self, position: int | None = None) -> bool:
        if position is None:
            position = self.input.cursor_position
        if (position >= 0) and (position < len(self.template)):
            return bool(self.template[position].flags & _CharFlags.SEPARATOR)
        else:
            return False

    def prev_separator_position(self, position: int | None = None) -> int | None:
        if position is None:
            position = self.input.cursor_position
        for index in range(position - 1, 0, -1):
            if self.template[index].flags & _CharFlags.SEPARATOR:
                return index
        else:
            return None

    def next_separator_position(self, position: int | None = None) -> int | None:
        if position is None:
            position = self.input.cursor_position
        for index in range(position + 1, len(self.template)):
            if self.template[index].flags & _CharFlags.SEPARATOR:
                return index
        else:
            return None

    def next_separator(self, position: int | None = None) -> str | None:
        position = self.next_separator_position(position)
        if position is None:
            return None
        else:
            return self.template[position].char

    def display(self, value: str) -> str:
        result = []
        for c, char_def in zip(value, self.template):
            if c == " ":
                c = char_def.char
            result.append(c)
        return "".join(result)

    def update_mask(self, placeholder: str) -> None:
        for index, char_def in enumerate(self.template):
            if (char_def.flags & _CharFlags.SEPARATOR) == 0:
                if index < len(placeholder):
                    char_def.char = placeholder[index]
                else:
                    char_def.char = self.blank

    @property
    def mask(self) -> str:
        return "".join([c.char for c in self.template])

    @property
    def empty_mask(self) -> str:
        return "".join(
            [
                " " if (c.flags & _CharFlags.SEPARATOR) == 0 else c.char
                for c in self.template
            ]
        )


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
        height: 3;
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

    cursor_blink = reactive(True, init=False)
    value: Reactive[str] = reactive("", layout=True, init=False)
    input_scroll_offset = reactive(0)
    cursor_position = reactive(0)
    view_position = reactive(0)
    placeholder = reactive("")
    complete = reactive("")
    width = reactive(1)
    _cursor_visible = reactive(True)
    password = reactive(False)
    suggester: Suggester | None
    """The suggester used to provide completions as the user types."""
    _suggestion = reactive("")
    """A completion suggestion for the current value in the input."""
    restrict = var["str | None"](None)
    """A regular expression to limit changes in value."""
    type = var[InputType]("text")
    """The type of the input."""
    max_length = var["int | None"](None)
    """The maximum length of the input, in characters."""
    valid_empty = var(False)
    """Empty values should pass validation."""
    template = var("")
    """Input template currently in use."""

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
        restrict: str | None = None,
        type: InputType = "text",
        max_length: int = 0,
        suggester: Suggester | None = None,
        validators: Validator | Iterable[Validator] | None = None,
        validate_on: Iterable[InputValidationOn] | None = None,
        valid_empty: bool = False,
        template: str = "",
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        tooltip: RenderableType | None = None,
    ) -> None:
        """Initialise the `Input` widget.

        Args:
            value: An optional default value for the input.
            placeholder: Optional placeholder text for the input.
            highlighter: An optional highlighter for the input.
            password: Flag to say if the field should obfuscate its content.
            restrict: A regex to restrict character inputs.
            type: The type of the input.
            max_length: The maximum length of the input, or 0 for no maximum length.
            suggester: [`Suggester`][textual.suggester.Suggester] associated with this
                input instance.
            validators: An iterable of validators that the Input value will be checked against.
            validate_on: Zero or more of the values "blur", "changed", and "submitted",
                which determine when to do input validation. The default is to do
                validation for all messages.
            valid_empty: Empty values are valid.
            template: Optional template string.
            name: Optional name for the input widget.
            id: Optional ID for the widget.
            classes: Optional initial classes for the widget.
            disabled: Whether the input is disabled or not.
            tooltip: Optional tooltip.
        """
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)

        self._blink_timer: Timer | None = None
        """Timer controlling the blinking of the cursor, instantiated in `on_mount`."""

        self._template: _Template | None = None

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
            self.validators = list(validators)

        self.validate_on = (
            set(validate_on) & _POSSIBLE_VALIDATE_ON_VALUES
            if validate_on is not None
            else _POSSIBLE_VALIDATE_ON_VALUES
        )
        """Set with event names to do input validation on.

        Validation can only be performed on blur, on input changes and on input submission.

        Example:
            This creates an `Input` widget that only gets validated when the value
            is submitted explicitly:

            ```py
            input = Input(validate_on=["submitted"])
            ```
        """
        self._reactive_valid_empty = valid_empty
        self._valid = True

        self.restrict = restrict
        if type not in _RESTRICT_TYPES:
            raise ValueError(
                f"Input type must be one of {friendly_list(_RESTRICT_TYPES.keys())}; not {type!r}"
            )
        self.type = type
        self.max_length = max_length
        if not self.validators:
            from ..validation import Integer, Number

            if self.type == "integer":
                self.validators.append(Integer())
            elif self.type == "number":
                self.validators.append(Number())

        if template:
            self._template = _Template(self, template)
        self.template = template

        if (value is not None) or (self._template is not None):
            if self._template is not None:
                value, _ = self._template.insert_separators(value or "", 0)
            self.value = value
        if tooltip is not None:
            self.tooltip = tooltip

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

    def validate_value(self, value: str) -> str:
        if self._template is None:
            return value
        if not self._template.check(value, True):
            raise ValueError("Value does not match template!")
        return value[: len(self._template.mask)]

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

        self.app.cursor_position = self.cursor_screen_offset

    def _watch_cursor_blink(self, blink: bool) -> None:
        """Ensure we handle updating the cursor blink at runtime."""
        if self._blink_timer is not None:
            if blink:
                self._blink_timer.resume()
            else:
                self._cursor_visible = True
                self._blink_timer.pause()

    @property
    def cursor_screen_offset(self) -> Offset:
        """The offset of the cursor of this input in screen-space. (x, y)/(column, row)"""
        x, y, _width, _height = self.content_region
        return Offset(x + self._cursor_offset - self.view_position, y)

    def _watch_value(self, value: str) -> None:
        self._suggestion = ""
        if self.suggester and value:
            self.run_worker(self.suggester._get_suggestion(self, value))
        if self.styles.auto_dimensions:
            self.refresh(layout=True)

        validation_result = (
            self.validate(value) if "changed" in self.validate_on else None
        )
        self.post_message(self.Changed(self, value, validation_result))

    def _watch_valid_empty(self) -> None:
        """Repeat validation when valid_empty changes."""
        self._watch_value(self.value)

    def _watch_template(self, template: str) -> None:
        """Revalidate when template changes."""
        self._template = _Template(self, template) if template else None
        if self.is_mounted:
            self._watch_value(self.value)

    def _watch_placeholder(self, placeholder: str) -> None:
        """Update template display mask when placeholder changes."""
        if self._template is not None:
            self._template.update_mask(placeholder)
            self.refresh()

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

        def set_classes() -> None:
            """Set classes for valid flag."""
            valid = self._valid
            self.set_class(not valid, "-invalid")
            self.set_class(valid, "-valid")

        validators = list(self.validators)
        if self._template is not None:
            validators.append(self._template)

        # If no validators are supplied, and therefore no validation occurs, we return None.
        if not validators:
            self._valid = True
            set_classes()
            return None

        if self.valid_empty and not value:
            self._valid = True
            set_classes()
            return None

        validation_results: list[ValidationResult] = [
            validator.validate(value) for validator in validators
        ]
        combined_result = ValidationResult.merge(validation_results)
        self._valid = combined_result.is_valid
        set_classes()

        return combined_result

    @property
    def is_valid(self) -> bool:
        """Check if the value has passed validation."""
        return self._valid

    @property
    def cursor_width(self) -> int:
        """The width of the input (with extra space for cursor at the end)."""
        if self.placeholder and not self.value:
            return cell_len(self.placeholder)
        return self._position_to_cell(len(self.value)) + 1

    def render(self) -> RenderResult:
        self.view_position = self.view_position
        if (not self.value) and (self._template is None):
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
            if self._template is None:
                value = self.value
            else:
                value = self._template.display(self.value)
            text = Text(value, no_wrap=True, overflow="ignore")
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
        self._blink_timer = self.set_interval(
            0.5,
            self._toggle_cursor,
            pause=not (self.cursor_blink and self.has_focus),
        )

    def _on_blur(self, _: Blur) -> None:
        self._blink_timer.pause()
        if "blur" in self.validate_on:
            self.validate(self.value)

    def _on_focus(self, _: Focus) -> None:
        self.cursor_position = len(self.value)
        if self.cursor_blink:
            self._blink_timer.resume()
        self.app.cursor_position = self.cursor_screen_offset
        self._suggestion = ""

    async def _on_key(self, event: events.Key) -> None:
        self._cursor_visible = True
        if self.cursor_blink:
            self._blink_timer.reset()

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
            cell_width = _cell_size(char)
            if cell_offset <= click_x < (cell_offset + cell_width):
                self.cursor_position = index
                break
            cell_offset += cell_width
        else:
            self.cursor_position = len(self.value)
        if (self._template is not None) and self._template.at_separator():
            self._template.move_cursor(1)

    async def _on_suggestion_ready(self, event: SuggestionReady) -> None:
        """Handle suggestion messages and set the suggestion when relevant."""
        if event.value == self.value:
            self._suggestion = event.suggestion

    def insert_text_at_cursor(self, text: str) -> None:
        """Insert new text at the cursor, move the cursor to the end of the new text.

        Args:
            text: New text to insert.
        """

        def check_allowed_value(value: str) -> bool:
            """Check if new value is restricted."""
            # Check max length
            if self.max_length and len(value) > self.max_length:
                return False
            # Check explicit restrict
            if self.restrict and re.fullmatch(self.restrict, value) is None:
                return False
            # Check type restrict
            if self.type:
                type_restrict = _RESTRICT_TYPES.get(self.type, None)
                if (
                    type_restrict is not None
                    and re.fullmatch(type_restrict, value) is None
                ):
                    return False
            # Character is allowed
            return True

        if self._template is not None:
            new_value = self._template.insert_text_at_cursor(text)
            if new_value is not None:
                new_value, cursor_position = new_value
                if check_allowed_value(new_value):
                    self.value = new_value
                    self.cursor_position = cursor_position
                else:
                    self.restricted()
            else:
                self.restricted()
        elif self.cursor_position >= len(self.value):
            new_value = self.value + text
            if check_allowed_value(new_value):
                self.value = new_value
                self.cursor_position = len(self.value)
            else:
                self.restricted()
        else:
            value = self.value
            before = value[: self.cursor_position]
            after = value[self.cursor_position :]
            new_value = f"{before}{text}{after}"
            if check_allowed_value(new_value):
                self.value = new_value
                self.cursor_position += len(text)
            else:
                self.restricted()

    def restricted(self) -> None:
        """Called when a character has been restricted.

        The default behavior is to play the system bell.
        You may want to override this method if you want to disable the bell or do something else entirely.
        """
        self.app.bell()

    def clear(self) -> None:
        """Clear the input."""
        if self._template is None:
            value, cursor_position = "", 0
        else:
            value, cursor_position = self._template.insert_separators("", 0)
        self.value = value
        self.cursor_position = cursor_position

    def action_cursor_left(self) -> None:
        """Move the cursor one position to the left."""
        if self._template is None:
            self.cursor_position -= 1
        else:
            self._template.move_cursor(-1)

    def action_cursor_right(self) -> None:
        """Accept an auto-completion or move the cursor one position to the right."""
        if self._cursor_at_end and self._suggestion:
            self.value = self._suggestion
            self.cursor_position = len(self.value)
        else:
            if self._template is None:
                self.cursor_position += 1
            else:
                self._template.move_cursor(1)

    def action_home(self) -> None:
        """Move the cursor to the start of the input."""
        if self._template is None:
            self.cursor_position = 0
        else:
            self._template.move_cursor(-len(self.template))

    def action_end(self) -> None:
        """Move the cursor to the end of the input."""
        self.cursor_position = len(self.value)

    _WORD_START = re.compile(r"(?<=\W)\w")

    def action_cursor_left_word(self) -> None:
        """Move the cursor left to the start of a word."""
        if self._template is not None:
            if self._template.at_separator(self.cursor_position - 1):
                position = self._template.prev_separator_position(
                    self.cursor_position - 1
                )
            else:
                position = self._template.prev_separator_position()
            if position:
                position += 1
            self.cursor_position = position or 0
        elif self.password:
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
        if self._template is not None:
            position = self._template.next_separator_position()
            if position is None:
                self.cursor_position = len(self._template.mask)
            else:
                self.cursor_position = position + 1
        elif self.password:
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
        if self._template is not None:
            self._template.delete_at_position()
        else:
            value = self.value
            delete_position = self.cursor_position
            before = value[:delete_position]
            after = value[delete_position + 1 :]
            self.value = f"{before}{after}"
            self.cursor_position = delete_position

    def action_delete_right_word(self) -> None:
        """Delete the current character and all rightward to the start of the next word."""
        if self._template:
            position = self._template.next_separator_position()
            if position is not None:
                position += 1
            else:
                position = len(self.value)
            for index in range(self.cursor_position, position):
                self.cursor_position = index
                if not self._template.at_separator():
                    self._template.delete_at_position()
        elif self.password:
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
        if self._template is not None:
            self._template.move_cursor(-1)
            self._template.delete_at_position()
        elif self.cursor_position == len(self.value):
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
        if self._template is not None:
            if self._template.at_separator(self.cursor_position - 1):
                position = self._template.prev_separator_position(
                    self.cursor_position - 1
                )
            else:
                position = self._template.prev_separator_position()
            if position:
                position += 1
            else:
                position = 0
            for index in range(position, self.cursor_position):
                self.cursor_position = index
                if not self._template.at_separator():
                    self._template.delete_at_position()
            self.cursor_position = position
        elif self.password:
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
            if self._template is not None:
                cursor_position = self.cursor_position
                if cursor_position >= len(self.value):
                    self.value = ""
                else:
                    self.value = (
                        self._template.empty_mask[:cursor_position]
                        + self.value[cursor_position:]
                    )
            else:
                self.value = self.value[self.cursor_position :]
            self.cursor_position = 0

    async def action_submit(self) -> None:
        """Handle a submit action.

        Normally triggered by the user pressing Enter. This may also run any validators.
        """
        validation_result = (
            self.validate(self.value) if "submitted" in self.validate_on else None
        )
        self.post_message(self.Submitted(self, self.value, validation_result))
