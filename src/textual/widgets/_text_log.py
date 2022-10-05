from __future__ import annotations

from typing import cast

from rich.console import RenderableType
from rich.highlighter import ReprHighlighter
from rich.pretty import Pretty
from rich.protocol import is_renderable
from rich.segment import Segment
from rich.text import Text

from ..reactive import var
from ..geometry import Size, Region
from ..scroll_view import ScrollView
from .._cache import LRUCache
from .._segment_tools import line_crop
from .._types import Lines


class TextLog(ScrollView, can_focus=True):
    DEFAULT_CSS = """    
    TextLog{
        background: $surface;
        color: $text;       
        overflow-y: scroll;
    }
    """

    max_lines: var[int | None] = var(None)
    min_width: var[int] = var(78)
    wrap: var[bool] = var(False)
    highlight: var[bool] = var(False)

    def __init__(
        self,
        *,
        max_lines: int | None = None,
        min_width: int = 78,
        wrap: bool = False,
        highlight: bool = False,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        self.max_lines = max_lines
        self.lines: list[list[Segment]] = []
        self._line_cache: LRUCache[tuple[int, int, int, int], list[Segment]]
        self._line_cache = LRUCache(1024)
        self.max_width: int = 0
        self.min_width = min_width
        self.wrap = wrap
        self.highlight = highlight
        self.highlighter = ReprHighlighter()
        super().__init__(name=name, id=id, classes=classes)

    def _on_styles_updated(self) -> None:
        self._line_cache.clear()

    def write(self, content: RenderableType | object) -> None:
        """Write text or a rich renderable.

        Args:
            content (RenderableType): Rich renderable (or text).
        """

        renderable: RenderableType
        if not is_renderable(content):
            renderable = Pretty(content)
        else:
            if isinstance(content, str):
                if self.highlight:
                    renderable = self.highlighter(content)
                else:
                    renderable = Text(content)
            else:
                renderable = cast(RenderableType, content)

        console = self.app.console
        width = max(self.min_width, self.size.width or self.min_width)

        render_options = console.options.update_width(width)
        if not self.wrap:
            render_options = render_options.update(overflow="ignore", no_wrap=True)
        segments = self.app.console.render(renderable, render_options)
        lines = list(Segment.split_lines(segments))
        self.max_width = max(
            self.max_width,
            max(sum(segment.cell_length for segment in _line) for _line in lines),
        )
        self.lines.extend(lines)

        if self.max_lines is not None:
            self.lines = self.lines[-self.max_lines :]
        self.virtual_size = Size(self.max_width, len(self.lines))
        self.scroll_end(animate=False, speed=100)

    def clear(self) -> None:
        """Clear the text log."""
        del self.lines[:]
        self.max_width = 0
        self.virtual_size = Size(self.max_width, len(self.lines))

    def render_line(self, y: int) -> list[Segment]:
        scroll_x, scroll_y = self.scroll_offset
        return self._render_line(scroll_y + y, scroll_x, self.size.width)

    def render_lines(self, crop: Region) -> Lines:
        """Render the widget in to lines.

        Args:
            crop (Region): Region within visible area to.

        Returns:
            Lines: A list of list of segments
        """
        lines = self._styles_cache.render_widget(self, crop)
        return lines

    def _render_line(self, y: int, scroll_x: int, width: int) -> list[Segment]:

        if y >= len(self.lines):
            return [Segment(" " * width, self.rich_style)]

        key = (y, scroll_x, width, self.max_width)
        if key in self._line_cache:
            return self._line_cache[key]

        line = self.lines[y]
        line = Segment.adjust_line_length(
            line, max(self.max_width, width), self.rich_style
        )
        line = line_crop(line, scroll_x, scroll_x + width, self.max_width)
        self._line_cache[key] = line
        return line
