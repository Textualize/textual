from __future__ import annotations

import os
from typing import ClassVar, FrozenSet, List, Tuple, Union

from rich.console import Console, ConsoleOptions, RenderableType, RenderResult
from rich.segment import Segment
from rich.style import Style
from rich.syntax import DEFAULT_THEME, Syntax

from .. import events
from .._segment_tools import line_crop
from ..binding import Binding, BindingType
from ..geometry import Offset, Size
from ..reactive import reactive
from ..scroll_view import ScrollView


class _Buffer:
    """
    A buffer.
    """

    def __init__(self) -> None:
        self._lines = [[]]

    def get_line_length(self, y: int) -> int:
        """
        Args:
            y: The line number.

        Returns:
            Length of line at y.
        """
        return len(self._lines[y])

    @property
    def max_y(self) -> int:
        """
        Returns:
            Number of the lines.
        """
        return len(self._lines)

    @property
    def max_x(self) -> int:
        """
        Returns:
            Length of the longest line.
        """
        if not self.max_y:
            return 0
        return max(len(line) for line in self._lines)

    @property
    def max_xy(self) -> Tuple[int, int]:
        return (self.max_x, self.max_y)

    def write(self, cursor_pad_at_lines: Union[FrozenSet[int], None] = None) -> str:
        """
        Write out the buffer.

        Args:
            cursor_pad_at_lines: Cursor pad at line numbers.

        Returns:
            The written buffer
        """
        lines = []
        has_cursor_pads = cursor_pad_at_lines is not None
        for index, line in enumerate(self._lines):
            line = "".join(line)
            if has_cursor_pads and index in cursor_pad_at_lines:
                line += " "
            lines.append(line)
        return os.linesep.join(lines)

    def insert(self, position: Offset, text: str) -> None:
        """
        Insert the text at position.

        Args:
            text: New text to insert.
        """
        x, y = position
        if text == os.linesep:
            line = self._lines[y][x:]
            self._lines.insert(y + 1, line)
            del self._lines[y][x:]
            return
        self._lines[y].insert(x, text)

    def delete_char(self, position: Offset) -> None:
        """
        Delete the character at position.

        Args:
            position: Position of the charcater
        """
        x, y = position
        del self._lines[y][x]

    def delete_linebreak(self, y: int) -> None:
        """
        Merge into the line at y above and delete the line at y.

        Args:
            y: The line number.
        """
        line = self._lines[y]
        self._lines[y - 1] += line
        del self._lines[y]


class _TextAreaRenderable:
    """Render the TextArea content"""

    def __init__(self, textarea: TextArea) -> None:
        self.textarea = textarea

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        def set_cursor(position: Offset, syntax: Syntax, style: Style):
            x, y = position
            y += 1
            syntax.stylize_range(style, (y, x), (y, x + 1))

        textarea = self.textarea
        lines_with_cursors = frozenset({textarea.cursor_offset.y})
        written_buffer = textarea._buffer.write(lines_with_cursors)
        syntax = Syntax(written_buffer, textarea._lexer)
        cursor_style = self.textarea.get_component_rich_style("textarea--cursor")

        self._set_background(syntax)
        set_cursor(textarea.cursor_offset, syntax, cursor_style)

        options.max_width = textarea._buffer.max_x + 1
        options.height = textarea._buffer.max_y

        lines = console.render_lines(syntax, options)
        scroll_x, scroll_y = textarea.scroll_offset
        lines = lines[scroll_y:]
        for line in lines:
            line = line_crop(
                line,
                scroll_x,
                scroll_x + textarea.size.width,
                Segment.get_line_length(line),
            )
            line.append(Segment.line())
            yield from line

    def _set_background(self, syntax: Syntax) -> None:
        bgcolor = syntax.get_theme(DEFAULT_THEME).get_background_style().bgcolor
        if bgcolor is None:
            return
        self.textarea.styles.background = bgcolor.name


# TODO: document code :)
# TODO: possibility to pass `pygments.lexer.Lexer` with "lexer" argument
# TODO: possibility to pass the theme for syntax highlighting
# TODO: implement tab (\t) support
# TODO: implement multiple cursors
class TextArea(ScrollView, can_focus=True):
    """
    A multi-line input widget.
    """

    BINDINGS: ClassVar[List[BindingType]] = [
        Binding("left", "cursor_left", "cursor left"),
        Binding("right", "cursor_right", "cursor right"),
        Binding("up", "cursor_up", "cursor up"),
        Binding("down", "cursor_down", "cursor down"),
        Binding("backspace", "delete_left", "delete left"),
        Binding("enter", "insert_linebreak_at_cursor", "insert linebreak"),
    ]
    """
    | Key(s) | Description |
    | :- | :- |
    | left | Move the cursor one character left. |
    | right | Move the cursor one character right. |
    | up | Move the cursor one line up. |
    | down | Move the cursor one line down. |
    | backspace | Delete the character to the left of the cursor. |
    | enter | Do a linebreak. |
    """

    COMPONENT_CLASSES: ClassVar[set[str]] = {"textarea--cursor"}
    """
    | Class | Description |
    | :- | :- |
    | `textarea--cursor` | Target the cursor. |
    """

    DEFAULT_CSS = """
    TextArea>.textarea--cursor {
        background: white;
        color: black;
    }
    """

    cursor_offset: reactive[Offset] = reactive(Offset(0, 0))
    cursor_x: reactive[int] = reactive(0)
    cursor_y: reactive[int] = reactive(0)

    def __init__(
        self,
        lexer: str | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        self._lexer = lexer or ""
        self._buffer = _Buffer()
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)

    def compute_cursor_offset(self) -> Offset:
        return Offset(self.cursor_x, self.cursor_y)

    def watch_cursor_offset(
        self, previous_cursor_offset: Offset, cursor_offset: Offset
    ) -> None:
        previous_cursor_x, _ = previous_cursor_offset
        _, cursor_y = cursor_offset
        line_length = self._buffer.get_line_length(cursor_y)
        if previous_cursor_x > line_length:
            self.cursor_x = line_length

    def validate_cursor_x(self, cursor_x: int) -> int:
        if cursor_x < 0:
            return 0
        line_length = self._buffer.get_line_length(self.cursor_y)
        if cursor_x > line_length:
            return line_length
        return cursor_x

    def validate_cursor_y(self, cursor_y: int) -> int:
        if cursor_y < 0:
            return 0
        last_line = self._buffer.max_y - 1
        if cursor_y > last_line:
            return last_line
        return cursor_y

    def action_cursor_left(self) -> None:
        self.cursor_x -= 1

    def action_cursor_right(self) -> None:
        self.cursor_x += 1

    def action_cursor_up(self) -> None:
        self.cursor_y -= 1

    def action_cursor_down(self) -> None:
        self.cursor_y += 1

    def action_delete_left(self) -> None:
        if not self.cursor_x and self.cursor_y:
            above_line_length = self._buffer.get_line_length(self.cursor_y - 1)
            self._buffer.delete_linebreak(self.cursor_y)
            self.action_cursor_up()
            self.cursor_x = above_line_length
            return
        if self.cursor_x:
            self.action_cursor_left()
            self._buffer.delete_char(self.cursor_offset)

    def action_insert_linebreak_at_cursor(self) -> None:
        self._buffer.insert(self.cursor_offset, os.linesep)
        self.action_cursor_down()
        self.cursor_x = 0

    def render(self) -> RenderableType:
        max_x, max_y = self._buffer.max_xy
        self.virtual_size = Size(max_x, max_y)
        return _TextAreaRenderable(self)

    def insert_text_at_cursor(self, text: str) -> None:
        self._buffer.insert(self.cursor_offset, text)
        self.action_cursor_right()

    async def _on_key(self, event: events.Key) -> None:
        # Do key bindings first
        if await self.handle_key(event):
            event.prevent_default()
            event.stop()
            return
        if event.is_printable:
            event.stop()
            assert event.character is not None
            self.insert_text_at_cursor(event.character)
            event.prevent_default()
