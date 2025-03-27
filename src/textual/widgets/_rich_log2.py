from __future__ import annotations

from dataclasses import dataclass, field
from itertools import islice

from rich.console import RenderableType

from textual.cache import LRUCache
from textual.reactive import var
from textual.scroll_view import ScrollView
from textual.strip import Strip
from textual.style import Style
from textual.visual import Visual, visualize


class _HeightMap:

    def __init__(self) -> None:
        self.lines: list[tuple[int, int]]
        self.item_to_line: dict[int, int] = {}
        self.item_heights: dict[int, int] = {}

    def get_line_range(self, line_no: int, count: int) -> list[tuple[int, int]]:
        return self.lines[line_no : line_no + count]

    def add_item(self, item_id: int, height: int) -> None:
        self.item_to_line[item_id] = len(self.lines)
        self.item_heights[item_id] = height
        new_lines = [(item_id, line_offset) for line_offset in range(height)]
        self.lines.extend(new_lines)

    def update_item(self, item_id: int, height: int) -> None:
        old_height = self.item_heights[item_id]
        line_start = self.item_to_line[item_id]
        self.item_heights[item_id] = height
        height_change = height - old_height
        if not height_change:
            return
        self.lines[line_start : line_start + old_height] = [
            (item_id, line_offset) for line_offset in range(height)
        ]
        for line_no, (item_id, line_offset) in enumerate(
            islice(self.lines, line_start + height, None), line_start + height
        ):
            if line_offset:
                self.item_to_line[item_id] = line_no


@dataclass
class _HeightBucket:
    start: int = 0
    height: int = 0
    items: list[tuple[int, int]] = field(default_factory=list)


class _HeightMap:
    def __init__(self, bucket_size: int = 100) -> None:
        self._bucket_size = bucket_size
        self._buckets: list[_HeightBucket] = [_HeightBucket()]
        self.height = 0

    def get_line_items(self, line_no: int, count: int) -> list[tuple[int, int]]:
        """Get lines items for a given line range.

        Args:
            line_no (_type_): _description_
            count (_type_): _description_

        Returns:
            List of tuples containing (ITEM ID, LINE OFFSET)
        """
        buckets = self._buckets
        bucket_no = len(self._buckets) // 2

        return []

    def add_item(self, item_id: int, height: int) -> None:
        line_no = self.height
        for line_offset in range(line_no, line_no + height):
            bucket = self._buckets[-1]
            if bucket.height >= self._bucket_size:
                bucket = _HeightBucket()
                self._buckets.append(bucket)
            bucket.items.append((item_id, line_offset))
        self.height += height


class RichLog(ScrollView, can_focus=True):
    DEFAULT_CSS = """
    RichLog{
        background: $surface;
        color: $foreground;
        overflow-y: scroll;
        &:focus {
            background-tint: $foreground 5%;
        }
    }
    """

    max_lines: var[int | None] = var(None)
    min_width: var[int] = var(78)
    markup: var[bool] = var(False)

    def __init__(
        self,
        *,
        max_lines: int | None = None,
        min_width: int = 78,
        markup: bool = False,
        auto_scroll: bool = True,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        """

        Args:
            max_lines: Maximum number of lines that may be scrolled, or `None` for no maximum.
            min_width: Minimum width of lines.
            markup: Enable content markup when writing text.
            auto_scroll. Automatically scroll to newly written text.
            name: The name of the widget.
            id: The ID of the widget in the DOM.
            classes: The CSS classes for the widget.
            disabled: Whether the widget is disabled or not.
        """
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self.max_lines = max_lines
        self.min_width = min_width
        self.markup = markup
        self.auto_scroll = auto_scroll

        self._item_id: int = 0
        self.items: dict[int, Visual] = {}
        # Cache key is (ITEM_ID, WIDTH, STYLE)
        self._renders: LRUCache[tuple[int, int, Style], list[Strip]] = LRUCache(
            maxsize=1024 * 2
        )
        self._height_map = _HeightMap()

    def _render_item(self, width: int, item_id: int, style: Style) -> list[Strip]:
        visual = self.items[item_id]
        strips = visual.to_strips(self, visual, width, None, style)
        self._renders[(item_id, width, style)] = strips
        return strips

    def write(self, content: Visual | RenderableType):
        visual = visualize(self, content, markup=self.markup)
        self.items[self._item_id] = visual
        self._item_id += 1
