from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar, Generic, TypeVar

import rich.repr
from rich.segment import Segment
from rich.style import Style
from rich.text import Text, TextType


from ..binding import Binding
from ..geometry import clamp, Region
from .._loop import loop_last
from .._cache import LRUCache
from ..reactive import reactive
from .._segment_tools import line_crop
from ..scroll_view import ScrollView

from .. import events

TreeDataType = TypeVar("TreeDataType")


@dataclass
class _TreeLine:
    parents: list[TreeNode]
    node: TreeNode
    last: bool


@rich.repr.auto
class TreeNode(Generic[TreeDataType]):
    def __init__(
        self,
        tree: Tree,
        parent: TreeNode[TreeDataType] | None,
        label: Text,
        data: TreeDataType,
        *,
        expanded: bool = True,
    ) -> None:
        self._tree = tree
        self._parent = parent
        self.label = label
        self.data: TreeDataType = data
        self.expanded = expanded
        self.children: list[TreeNode] = []

    def __rich_repr__(self) -> rich.repr.Result:
        yield self.label.plain
        yield self.data

    @property
    def last(self) -> bool:
        if self._parent is None:
            return True
        return bool(
            self._parent.children and self._parent.children[-1] == self,
        )

    def add(
        self, label: TextType, data: TreeDataType, expanded: bool = True
    ) -> TreeNode[TreeDataType]:
        if isinstance(label, str):
            text_label = Text.from_markup(label)
        else:
            text_label = label
        node = TreeNode(
            self._tree,
            self,
            text_label,
            data,
            expanded=expanded,
        )
        self.children.append(node)
        self._tree.invalidate()
        return node


class Tree(Generic[TreeDataType], ScrollView, can_focus=True):

    BINDINGS = [
        Binding("up", "cursor_up", "Cursor Up"),
        Binding("down", "cursor_down", "Cursor Down"),
    ]

    DEFAULT_CSS = """
    Tree {
        background: $surface;
        color: $text;
    }
    Tree > .tree--guides {
        color: $success;
    }
    Tree > .tree--cursor {
        background: $secondary;
        color: $text;
    }
    Tree > .tree--highlight {
        
        text-style: underline;
    }
    
    """

    show_root = reactive(True)

    COMPONENT_CLASSES: ClassVar[set[str]] = {
        "tree--guides",
        "tree--cursor",
        "tree--highlight",
    }

    hover_line = reactive(-1, repaint=False)
    cursor_line = reactive(0, repaint=False)

    def __init__(
        self,
        label: TextType,
        data: TreeDataType,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        if isinstance(label, str):
            text_label = Text.from_markup(label)
        else:
            text_label = label

        self.root: TreeNode[TreeDataType] = TreeNode(
            self, None, text_label, data, expanded=True
        )
        self._tree_lines_cached: list[_TreeLine] | None = None

    def validate_cursor_line(self, value: int) -> int:
        return clamp(value, 0, len(self._tree_lines) - 1)

    def invalidate(self) -> None:
        self._tree_lines_cached = None

    def _on_mouse_move(self, event: events.MouseMove):
        meta = event.style.meta

        if meta and "line" in meta:
            self.hover_line = meta["line"]
        else:
            self.hover_line = -1

    def watch_hover_line(self, previous_hover_line: int, hover_line: int) -> None:
        self.refresh_line(previous_hover_line)
        self.refresh_line(hover_line)

    def watch_cursor_line(self, previous_cursor: int, cursor: int) -> None:
        self.refresh_line(previous_cursor)
        self.refresh_line(cursor)

    def refresh_line(self, line: int) -> None:
        region = Region(0, line - self.scroll_offset.y, self.size.width, 1)
        if not self.window_region.overlaps(region):
            return
        self.refresh(region)

    @property
    def _tree_lines(self) -> list[_TreeLine]:
        if self._tree_lines_cached is None:
            self._build()
        assert self._tree_lines_cached is not None
        return self._tree_lines_cached

    def _build(self) -> None:

        lines: list[_TreeLine] = []
        add_line = lines.append

        root = self.root

        def add_node(path: list[TreeNode], node: TreeNode, last: bool) -> None:

            add_line(_TreeLine(path, node, last))

            if node.expanded:
                child_path = [*path, node]
                for last, child in loop_last(node.children):
                    add_node(child_path, child, last=last)

        add_node([], root, True)
        self._tree_lines_cached = lines

    def render_line(self, y: int) -> list[Segment]:
        width, height = self.size
        scroll_x, scroll_y = self.scroll_offset
        y += scroll_y
        style = self.rich_style
        return self._render_line(y, scroll_x, scroll_x + width, style)

    def _render_line(
        self, y: int, x1: int, x2: int, base_style: Style
    ) -> list[Segment]:
        tree_lines = self._tree_lines
        width = self.size.width

        if y >= len(tree_lines):
            return [Segment(" " * width, base_style)]

        style = base_style

        line = tree_lines[y]

        guide_style = base_style + self.get_component_rich_style("tree--guides")
        guides = Text.assemble(
            *[
                ("    " if node.last else "│   ", guide_style)
                for node in line.parents[1:]
            ]
        )
        if line.parents:
            if line.last:
                guides.append("└── ", style=guide_style)
            else:
                guides.append("├── ", style=guide_style)
        label = line.node.label.copy()
        if self.hover_line == y:
            label.stylize(self.get_component_rich_style("tree--highlight"))
        if self.cursor_line == y and self.has_focus:
            label.stylize(self.get_component_rich_style("tree--cursor"))
        label.stylize(Style(meta={"line": y}))

        guides.append(label)

        segments = list(guides.render(self.app.console))
        segments = Segment.adjust_line_length(segments, width, style=style)
        segments = list(Segment.apply_style(segments, style))
        segments = line_crop(segments, x1, x2, width)
        simplified_segments = list(Segment.simplify(segments))

        return simplified_segments

    def action_cursor_up(self) -> None:
        self.cursor_line -= 1

    def action_cursor_down(self) -> None:
        self.cursor_line += 1
