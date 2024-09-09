"""Provides a scrollable text-logging widget."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional, cast

from rich.console import RenderableType
from rich.highlighter import Highlighter, ReprHighlighter
from rich.measure import measure_renderables
from rich.pretty import Pretty
from rich.protocol import is_renderable
from rich.segment import Segment
from rich.text import Text

from textual.events import Resize

from ..cache import LRUCache
from ..geometry import Size
from ..reactive import var
from ..scroll_view import ScrollView
from ..strip import Strip

if TYPE_CHECKING:
    from typing_extensions import Self


class RichLog(ScrollView, can_focus=True):
    """A widget for logging text."""

    DEFAULT_CSS = """
    RichLog{
        background: $surface;
        color: $text;
        overflow-y: scroll;
    }
    """

    max_lines: var[int | None] = var[Optional[int]](None)
    min_width: var[int] = var(78)
    wrap: var[bool] = var(False)
    highlight: var[bool] = var(False)
    markup: var[bool] = var(False)
    auto_scroll: var[bool] = var(True)

    def __init__(
        self,
        *,
        max_lines: int | None = None,
        min_width: int = 78,
        wrap: bool = False,
        highlight: bool = False,
        markup: bool = False,
        auto_scroll: bool = True,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        """Create a RichLog widget.

        Args:
            max_lines: Maximum number of lines in the log or `None` for no maximum.
            min_width: Minimum width of renderables.
            wrap: Enable word wrapping (default is off).
            highlight: Automatically highlight content.
            markup: Apply Rich console markup.
            auto_scroll: Enable automatic scrolling to end.
            name: The name of the text log.
            id: The ID of the text log in the DOM.
            classes: The CSS classes of the text log.
            disabled: Whether the text log is disabled or not.
        """
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self.max_lines = max_lines
        """Maximum number of lines in the log or `None` for no maximum."""
        self._start_line: int = 0
        self.lines: list[Strip] = []
        self._line_cache: LRUCache[tuple[int, int, int, int], Strip]
        self._line_cache = LRUCache(1024)
        self.min_width = min_width
        """Minimum width of renderables."""
        self.wrap = wrap
        """Enable word wrapping."""
        self.highlight = highlight
        """Automatically highlight content."""
        self.markup = markup
        """Apply Rich console markup."""
        self.auto_scroll = auto_scroll
        """Automatically scroll to the end on write."""
        self.highlighter: Highlighter = ReprHighlighter()
        """Rich Highlighter used to highlight content when highlight is True"""

        self._widest_line_width = 0
        """The width of the widest line currently in the log."""

    def notify_style_update(self) -> None:
        self._line_cache.clear()

    def on_mount(self) -> None:
        print("mounting!")

    def on_resize(self, event: Resize) -> None:
        print("resize", event)

    def _make_renderable(self, content: RenderableType | object) -> RenderableType:
        """Make content renderable.

        Args:
            content: Content to render.

        Returns:
            A Rich renderable.
        """
        renderable: RenderableType
        if not is_renderable(content):
            renderable = Pretty(content)
        else:
            if isinstance(content, str):
                if self.markup:
                    renderable = Text.from_markup(content)
                else:
                    renderable = Text(content)
                if self.highlight:
                    renderable = self.highlighter(renderable)
            else:
                renderable = cast(RenderableType, content)

        if isinstance(renderable, Text):
            renderable.expand_tabs()

        return renderable

    def write(
        self,
        content: RenderableType | object,
        width: int | None = None,
        expand: bool = False,
        shrink: bool = True,
        scroll_end: bool | None = None,
    ) -> Self:
        """Write a string or a Rich renderable to the log.

        Args:
            content: Rich renderable (or a string).
            width: Width to render or `None` to use optimal width.
                If a `min_width` is specified on the widget, then the width will be
                expanded to be at least `min_width`.
            expand: Enable expand to widget width, or `False` to use `width`.
                If `width` is not `None`, then `expand` will be ignored.
            shrink: Enable shrinking of content to fit width.
                If `width` is not `None`, then `shrink` will be ignored.
            scroll_end: Enable automatic scroll to end, or `None` to use `self.auto_scroll`.

        Returns:
            The `RichLog` instance.
        """

        auto_scroll = self.auto_scroll if scroll_end is None else scroll_end

        console = self.app.console
        render_options = console.options

        renderable = self._make_renderable(content)

        if isinstance(renderable, Text) and not self.wrap:
            render_options = render_options.update(overflow="ignore", no_wrap=True)

        if width is not None:
            # Use the width specified by the caller.
            # Note that we ignore `expand` and `shrink` when a width is specified.
            render_width = width
        else:
            # Compute the width based on available information.
            renderable_width = measure_renderables(
                console, render_options, [renderable]
            ).maximum

            render_width = renderable_width
            scrollable_content_width = self.scrollable_content_region.width

            if expand:
                # Expand the renderable to the width of the scrollable content region.
                render_width = max(renderable_width, scrollable_content_width)

            if shrink and not expand:
                # Shrink the renderable down to fit within the scrollable content region.
                render_width = min(renderable_width, scrollable_content_width)

        # Ensure we don't render below the minimum width.
        render_width = max(render_width, self.min_width)
        render_options = render_options.update_width(render_width)

        # Render into possibly wrapped lines.
        segments = self.app.console.render(renderable, render_options)
        lines = list(Segment.split_lines(segments))

        if not lines:
            self._widest_line_width = max(render_width, self._widest_line_width)
            self.lines.append(Strip.blank(render_width))
        else:
            strips = Strip.from_lines(lines)
            for strip in strips:
                strip.adjust_cell_length(render_width)
            self.lines.extend(strips)

            if self.max_lines is not None and len(self.lines) > self.max_lines:
                self._start_line += len(self.lines) - self.max_lines
                self.refresh()
                self.lines = self.lines[-self.max_lines :]

            # Compute the width after wrapping and trimming
            # TODO - this is wrong because if we trim a long line, the max width
            #  could decrease, but we don't look at which lines were trimmed here.
            self._widest_line_width = max(
                self._widest_line_width,
                max(sum([segment.cell_length for segment in _line]) for _line in lines),
            )

        # Update the virtual size - the width may have changed after adding
        # the new line(s), and the height will definitely have changed.
        self.virtual_size = Size(self._widest_line_width, len(self.lines))

        if auto_scroll:
            self.scroll_end(animate=False)

        return self

    def clear(self) -> Self:
        """Clear the text log.

        Returns:
            The `RichLog` instance.
        """
        self.lines.clear()
        self._line_cache.clear()
        self._start_line = 0
        self.virtual_size = Size(0, len(self.lines))
        self.refresh()
        return self

    def render_line(self, y: int) -> Strip:
        scroll_x, scroll_y = self.scroll_offset
        line = self._render_line(
            scroll_y + y, scroll_x, self.scrollable_content_region.width
        )
        strip = line.apply_style(self.rich_style)
        return strip

    def _render_line(self, y: int, scroll_x: int, width: int) -> Strip:
        if y >= len(self.lines):
            return Strip.blank(width, self.rich_style)

        key = (y + self._start_line, scroll_x, width, self._widest_line_width)
        if key in self._line_cache:
            return self._line_cache[key]

        line = self.lines[y].crop_extend(scroll_x, scroll_x + width, self.rich_style)

        self._line_cache[key] = line
        return line
