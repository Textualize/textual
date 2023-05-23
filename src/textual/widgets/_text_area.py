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
    def __init__(self) -> None:
        self._lines = [[]]

    def get_line_length(self, y: int) -> int:
        return len(self._lines[y])

    @property
    def max_y(self) -> int:
        return len(self._lines)

    @property
    def max_x(self) -> int:
        if not self.max_y:
            return 0
        return max(len(line) for line in self._lines)

    @property
    def max_xy(self) -> Tuple[int, int]:
        return (self.max_x, self.max_y)

    def write(self, cursor_pad_at_lines: Union[FrozenSet[int], None] = None) -> str:
        lines: List[str] = []
        has_cursor_pads = cursor_pad_at_lines is not None
        for index, line in enumerate(self._lines):
            line = "".join(line)
            if has_cursor_pads and index in cursor_pad_at_lines:
                line += " "
            lines.append(line)
        return os.linesep.join(lines)

    def insert(self, position: Offset, text: str) -> None:
        x, y = position
        if text == os.linesep:
            line = self._lines[y][x:]
            self._lines.insert(y + 1, line)
            del self._lines[y][x:]
            return
        self._lines[y].insert(x, text)

    def remove_char(self, position: Offset) -> None:
        x, y = position
        del self._lines[y][x]

    def remove_linebreak(self, y: int) -> None:
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
        textarea = self.textarea

        options.max_width = textarea._buffer.max_x + 1
        options.height = textarea._buffer.max_y

        lines_with_cursors = frozenset({textarea.cursor_offset.y})
        written_buffer = textarea._buffer.write(lines_with_cursors)
        syntax = Syntax(written_buffer, "python")
        cursor_style = self.textarea.get_component_rich_style("textarea--cursor")

        self._set_background(syntax)
        self._set_cursor(textarea.cursor_offset, syntax, cursor_style)

        scroll_x, scroll_y = textarea.scroll_offset
        lines = console.render_lines(syntax, options)
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

    def _set_cursor(self, position: Offset, syntax: Syntax, style: Style) -> None:
        x, y = position
        y += 1
        syntax.stylize_range(style, (y, x), (y, x + 1))

    def _set_background(self, syntax: Syntax) -> None:
        bgcolor = syntax.get_theme(DEFAULT_THEME).get_background_style().bgcolor
        if bgcolor is None:
            return
        self.textarea.styles.background = bgcolor.name


# FIXME: cursor jumping between odd lines (in terms of length)
# TODO: implement tab (\t) support
class TextArea(ScrollView, can_focus=True):
    BINDINGS: ClassVar[List[BindingType]] = [
        Binding("left", "cursor_left", "cursor left"),
        Binding("right", "cursor_right", "cursor right"),
        Binding("up", "cursor_up", "cursor up"),
        Binding("down", "cursor_down", "cursor down"),
        Binding("backspace", "remove_left", "remove left"),
        Binding("enter", "insert_linebreak_at_cursor", "insert linebreak"),
    ]

    COMPONENT_CLASSES: ClassVar[set[str]] = {"textarea--cursor"}

    DEFAULT_CSS = """
    TextArea>.textarea--cursor {
        background: white;
        color: black;
    }
    """
    cursor_offset: reactive[Offset] = reactive(Offset(0, 0))
    cursor_x: reactive[int] = reactive(0)
    cursor_y: reactive[int] = reactive(0)

    def __init__(self) -> None:
        self._buffer = _Buffer()
        super().__init__()

    def compute_cursor_offset(self) -> Offset:
        return Offset(self.cursor_x, self.cursor_y)

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

    def action_remove_left(self) -> None:
        if not self.cursor_x and self.cursor_y:
            above_line_length = self._buffer.get_line_length(self.cursor_y - 1)
            self._buffer.remove_linebreak(self.cursor_y)
            self.action_cursor_up()
            self.cursor_x = above_line_length
            return

        if self.cursor_x:
            self.action_cursor_left()
            self._buffer.remove_char(self.cursor_offset)

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
