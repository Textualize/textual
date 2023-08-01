from __future__ import annotations

import re
from typing import TYPE_CHECKING, Iterable, Optional

from rich.cells import cell_len
from rich.highlighter import ReprHighlighter
from rich.segment import Segment
from rich.text import Text

from .. import work
from .._cache import LRUCache
from ..geometry import Size
from ..reactive import var
from ..scroll_view import ScrollView
from ..strip import Strip

if TYPE_CHECKING:
    from typing_extensions import Self

_sub_escape = re.compile("[\u0000-\u0014]").sub


class Log(ScrollView, can_focus=True):
    """A widget to log text."""

    DEFAULT_CSS = """
    Log {
        background: $surface;
        color: $text;
        overflow: scroll;
    }
    """

    max_lines: var[int | None] = var[Optional[int]](None)
    """Maximum number of lines to show"""

    auto_scroll: var[bool] = var(True)
    """Automatically scroll to new lines."""

    def __init__(
        self,
        highlight: bool = False,
        max_lines: int | None = None,
        auto_scroll: bool = True,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        """Create a Log widget.

        Args:
            highlight: Enable highlighting.
            max_lines: Maximum number of lines to display.
            auto_scroll: Scroll to end on new lines.
            name: The name of the text log.
            id: The ID of the text log in the DOM.
            classes: The CSS classes of the text log.
            disabled: Whether the text log is disabled or not.
        """
        self.highlight = highlight
        self.max_lines = max_lines
        self.auto_scroll = auto_scroll
        self.lines: list[str] = []
        self._width = 0
        self._updates = 0
        self._render_line_cache: LRUCache[int, Strip] = LRUCache(1024)
        self.highlighter = ReprHighlighter()
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)

    def notify_style_update(self) -> None:
        self._render_line_cache.clear()

    def _update_maximum_width(self, updates: int, size: int) -> None:
        """Update the virtual size width.

        Args:
            updates: A counter of updates.
            size: Maximum size of new lines.
        """
        if updates == self._updates:
            self._width = max(size, self._width)
            self.virtual_size = Size(self._width, len(self.lines))

    @work(thread=True)
    def _update_size(self, updates: int, lines: list[str]) -> None:
        """A thread worker to update the width in the background.

        Args:
            updates: The update index at the time of invocation.
            lines: Lines that were added.
        """
        max_length = max(cell_len(line) for line in lines)
        self.app.call_from_thread(self._update_maximum_width, updates, max_length)

    def write_line(self, line: str) -> Self:
        """Write content on a new line.

        Args:
            line: String to write to the log.

        Returns:
            The `Log` instance.
        """
        self.write_lines([line])
        return self

    def write_lines(
        self,
        lines: Iterable[str],
        scroll_end: bool | None = None,
    ) -> Self:
        """Write an iterable of lines.

        Args:
            lines: An iterable of strings to write.
            scroll_end: Scroll to the end after writing, or `None` to use `self.auto_scroll`.

        Returns:
            The `Log` instance.
        """
        auto_scroll = self.auto_scroll if scroll_end is None else scroll_end
        new_lines = []
        for line in lines:
            new_lines.extend(line.splitlines())
        self.lines.extend(new_lines)
        if self.max_lines is not None and len(self.lines) > self.max_lines:
            del self.lines[: -self.max_lines]
        self.virtual_size = Size(self._width, len(self.lines))
        self._update_size(self._updates, new_lines)
        if auto_scroll:
            self.scroll_end(animate=False)
        return self

    def clear(self) -> Self:
        """Clear the Log.

        Returns:
            The `Log` instance.
        """
        self.lines.clear()
        self._width = 0
        self._render_line_cache.clear()
        self._updates += 1
        self.virtual_size = Size(0, 0)
        return self

    def render_line(self, y: int) -> Strip:
        """Render a line of content.

        Args:
            y: Y Coordinate of line.

        Returns:
            A rendered line.
        """
        scroll_x, scroll_y = self.scroll_offset
        strip = self._render_line(scroll_y + y, scroll_x, self.size.width)
        return strip

    def _render_line(self, y: int, scroll_x: int, width: int) -> Strip:
        if y >= len(self.lines):
            return Strip.blank(width, self.rich_style)

        line = self._render_line_strip(y)
        self._width = max(line.cell_length, self._width)
        self.virtual_size = Size(self._width, len(self.lines))
        line = line.adjust_cell_length(max(self._width, width), self.rich_style).crop(
            scroll_x, scroll_x + width
        )
        return line

    def _render_line_strip(self, y: int) -> Strip:
        if y in self._render_line_cache:
            return self._render_line_cache[y]

        _line = _sub_escape("�", self.lines[y].expandtabs())

        if self.highlight:
            line_text = self.highlighter(
                Text(_line, style=self.rich_style, no_wrap=True)
            )
            line = Strip(line_text.render(self.app.console))
        else:
            line = Strip([Segment(_line, self.rich_style)])
        self._render_line_cache[y] = line
        return line
