from __future__ import annotations

import re
from dataclasses import dataclass
from enum import IntFlag
from typing import TYPE_CHECKING, Iterable, Pattern

from rich.console import Console, ConsoleOptions, RenderableType
from rich.console import RenderResult as RichRenderResult
from rich.segment import Segment
from rich.text import Text
from typing_extensions import Literal

from .. import events
from .._segment_tools import line_crop

if TYPE_CHECKING:
    from ..app import RenderResult

from ..reactive import var
from ..validation import ValidationResult, Validator
from ._input import Input

InputValidationOn = Literal["blur", "changed", "submitted"]
"""Possible messages that trigger input validation."""


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
        style = input.get_component_rich_style("input--placeholder")
        result += Text(
            template.mask[value_length:],
            style,
        )
        for index, (c, char_def) in enumerate(zip(value, template.template)):
            if c == " ":
                result.stylize(style, index, index + 1)

        if self.cursor_visible and input.has_focus:
            if input._cursor_at_end:
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


class MaskedInput(Input, can_focus=True):
    """A masked text input widget."""

    template = var("")
    """Input template mask currently in use."""

    def __init__(
        self,
        template: str,
        value: str | None = None,
        placeholder: str = "",
        *,
        validators: Validator | Iterable[Validator] | None = None,
        validate_on: Iterable[InputValidationOn] | None = None,
        valid_empty: bool = False,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        tooltip: RenderableType | None = None,
    ) -> None:
        """Initialise the `Input` widget.

        Args:
            template: Template string.
            value: An optional default value for the input.
            placeholder: Optional placeholder text for the input.
            validators: An iterable of validators that the MaskedInput value will be checked against.
            validate_on: Zero or more of the values "blur", "changed", and "submitted",
                which determine when to do input validation. The default is to do
                validation for all messages.
            valid_empty: Empty values are valid.
            name: Optional name for the masked input widget.
            id: Optional ID for the widget.
            classes: Optional initial classes for the widget.
            disabled: Whether the input is disabled or not.
            tooltip: Optional tooltip.
        """
        self._template: _Template = None
        super().__init__(
            placeholder=placeholder,
            validators=validators,
            validate_on=validate_on,
            valid_empty=valid_empty,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )

        self._template = _Template(self, template)
        self.template = template

        value, _ = self._template.insert_separators(value or "", 0)
        self.value = value
        if tooltip is not None:
            self.tooltip = tooltip

    def validate_value(self, value: str) -> str:
        if self._template is None:
            return value
        if not self._template.check(value, True):
            raise ValueError("Value does not match template!")
        return value[: len(self._template.mask)]

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
        """Run all the validators associated with this MaskedInput on the supplied value.

        Same as `Input.validate()` but also validates against template which acts as an
        additional implicit validator.

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

        result = super().validate(value)
        validation_results: list[ValidationResult] = [self._template.validate(value)]
        if result is not None:
            validation_results.append(result)
        combined_result = ValidationResult.merge(validation_results)
        self._valid = combined_result.is_valid
        set_classes()

        return combined_result

    def render(self) -> RenderResult:
        return _InputRenderable(self, self._cursor_visible)

    @property
    def _value(self) -> Text:
        """Value rendered as text."""
        value = self._template.display(self.value)
        return Text(value, no_wrap=True, overflow="ignore")

    async def _on_click(self, event: events.Click) -> None:
        await super()._on_click(event)
        if self._template.at_separator():
            self._template.move_cursor(1)

    def insert_text_at_cursor(self, text: str) -> None:
        """Insert new text at the cursor, move the cursor to the end of the new text.

        Args:
            text: New text to insert.
        """

        new_value = self._template.insert_text_at_cursor(text)
        if new_value is not None:
            self.value, self.cursor_position = new_value
        else:
            self.restricted()

    def clear(self) -> None:
        """Clear the masked input."""
        self.value, self.cursor_position = self._template.insert_separators("", 0)

    def action_cursor_left(self) -> None:
        """Move the cursor one position to the left."""
        self._template.move_cursor(-1)

    def action_cursor_right(self) -> None:
        """Accept an auto-completion or move the cursor one position to the right."""
        self._template.move_cursor(1)

    def action_home(self) -> None:
        """Move the cursor to the start of the input."""
        self._template.move_cursor(-len(self.template))

    def action_cursor_left_word(self) -> None:
        """Move the cursor left to the start of a word."""
        if self._template.at_separator(self.cursor_position - 1):
            position = self._template.prev_separator_position(self.cursor_position - 1)
        else:
            position = self._template.prev_separator_position()
        if position:
            position += 1
        self.cursor_position = position or 0

    def action_cursor_right_word(self) -> None:
        """Move the cursor right to the start of a word."""
        position = self._template.next_separator_position()
        if position is None:
            self.cursor_position = len(self._template.mask)
        else:
            self.cursor_position = position + 1

    def action_delete_right(self) -> None:
        """Delete one character at the current cursor position."""
        self._template.delete_at_position()

    def action_delete_right_word(self) -> None:
        """Delete the current character and all rightward to the start of the next word."""
        position = self._template.next_separator_position()
        if position is not None:
            position += 1
        else:
            position = len(self.value)
        for index in range(self.cursor_position, position):
            self.cursor_position = index
            if not self._template.at_separator():
                self._template.delete_at_position()

    def action_delete_left(self) -> None:
        """Delete one character to the left of the current cursor position."""
        if self.cursor_position <= 0:
            # Cursor at the start, so nothing to delete
            return
        self._template.move_cursor(-1)
        self._template.delete_at_position()

    def action_delete_left_word(self) -> None:
        """Delete leftward of the cursor position to the start of a word."""
        if self.cursor_position <= 0:
            return
        if self._template.at_separator(self.cursor_position - 1):
            position = self._template.prev_separator_position(self.cursor_position - 1)
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

    def action_delete_left_all(self) -> None:
        """Delete all characters to the left of the cursor position."""
        if self.cursor_position > 0:
            cursor_position = self.cursor_position
            if cursor_position >= len(self.value):
                self.value = ""
            else:
                self.value = (
                    self._template.empty_mask[:cursor_position]
                    + self.value[cursor_position:]
                )
            self.cursor_position = 0
