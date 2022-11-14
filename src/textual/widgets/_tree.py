from __future__ import annotations

from dataclasses import dataclass
from operator import attrgetter
from typing import ClassVar, Generic, NewType, TypeVar

import rich.repr
from rich.segment import Segment
from rich.style import Style
from rich.text import Text, TextType


from ..binding import Binding
from ..geometry import clamp, Region, Size
from .._loop import loop_last
from .._cache import LRUCache
from ..reactive import reactive
from .._segment_tools import line_crop, line_pad
from ..scroll_view import ScrollView

from .. import events

NodeID = NewType("NodeID", int)
TreeDataType = TypeVar("TreeDataType")


@dataclass
class _TreeLine:
    path: list[TreeNode]
    last: bool

    @property
    def node(self) -> TreeNode:
        return self.path[-1]

    @property
    def line_width(self) -> int:
        return (len(self.path) * 4) + self.path[-1].label.cell_len - 4


@rich.repr.auto
class TreeNode(Generic[TreeDataType]):
    def __init__(
        self,
        tree: Tree,
        parent: TreeNode[TreeDataType] | None,
        id: NodeID,
        label: Text,
        data: TreeDataType,
        *,
        expanded: bool = True,
    ) -> None:
        self._tree = tree
        self._parent = parent
        self.id = id
        self.label = label
        self.data: TreeDataType = data
        self.expanded = expanded
        self.children: list[TreeNode] = []

        self._hover = False
        self._selected = False

    def __rich_repr__(self) -> rich.repr.Result:
        yield self.label.plain
        yield self.data

    @property
    def last(self) -> bool:
        """Check if this is the last child.

        Returns:
            bool: True if this is the last child, otherwise False.
        """
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
        node = self._tree._add_node(self, text_label, data)
        node.expanded = expanded
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
        background: $panel;
        color: $text;
    }
    Tree > .tree--label {
        
    }
    Tree > .tree--guides {
        color: $success;
    }


    Tree > .tree--guides-hover {  
        color: $success;      
        text-style: uu;
    }

    Tree > .tree--guides-selected {
        color: $warning;
        text-style: bold;
    }    

    Tree > .tree--cursor {
        background: $secondary;
        color: $text;
        text-style: bold;
    }

    Tree > .tree--highlight {        
        text-style: underline;
    }
    
    """

    show_root = reactive(True)

    COMPONENT_CLASSES: ClassVar[set[str]] = {
        "tree--label",
        "tree--guides",
        "tree--guides-hover",
        "tree--guides-selected",
        "tree--cursor",
        "tree--highlight",
    }

    hover_line: reactive[int] = reactive(-1, repaint=False)
    cursor_line: reactive[int] = reactive(0, repaint=False)

    LINES: dict[str, tuple[str, str, str, str]] = {
        "default": (
            "    ",
            "│   ",
            "└── ",
            "├── ",
        ),
        "bold": (
            "    ",
            "┃   ",
            "┗━━ ",
            "┣━━ ",
        ),
        "double": (
            "    ",
            "║   ",
            "╚══ ",
            "╠══ ",
        ),
    }

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

        self._nodes: dict[NodeID, TreeNode[TreeDataType]] = {}
        self._current_id = 0
        self.root = self._add_node(None, text_label, data)
        self.root.expanded = True
        self._tree_lines_cached: list[_TreeLine] | None = None

    def _add_node(
        self, parent: TreeNode[TreeDataType] | None, label: Text, data: TreeDataType
    ) -> TreeNode[TreeDataType]:
        node = TreeNode(self, parent, self._new_id(), label, data)
        self._nodes[node.id] = node
        return node

    def clear(self) -> None:
        """Clear all nodes under root."""
        self._tree_lines_cached = None
        self._current_id = 0
        root_label = self.root.label
        root_data = self.root.data
        self.root = TreeNode(
            self,
            None,
            self._new_id(),
            root_label,
            root_data,
            expanded=True,
        )
        self.refresh()

    def validate_cursor_line(self, value: int) -> int:
        return clamp(value, 0, len(self._tree_lines) - 1)

    def invalidate(self) -> None:
        self._tree_lines_cached = None
        self.refresh()

    def _on_mouse_move(self, event: events.MouseMove):
        meta = event.style.meta
        if meta and "line" in meta:
            self.hover_line = meta["line"]
        else:
            self.hover_line = -1

    def _new_id(self) -> NodeID:
        """Create a new node ID.

        Returns:
            NodeID: A unique node ID.
        """
        id = self._current_id
        self._current_id += 1
        return NodeID(id)

    def _get_node(self, line: int) -> TreeNode[TreeDataType] | None:
        try:
            tree_line = self._tree_lines[line]
        except IndexError:
            return None
        else:
            return tree_line.node

    def watch_hover_line(self, previous_hover_line: int, hover_line: int) -> None:
        previous_node = self._get_node(previous_hover_line)
        if previous_node is not None:
            self._refresh_node(previous_node)
            previous_node._hover = False

        node = self._get_node(hover_line)
        if node is not None:
            self._refresh_node(node)
            node._hover = True

    def watch_cursor_line(self, previous_line: int, line: int) -> None:
        previous_node = self._get_node(previous_line)
        if previous_node is not None:
            self._refresh_node(previous_node)
            previous_node._selected = False

        node = self._get_node(line)
        if node is not None:
            self._refresh_node(node)
            self.scroll_to_line(line)
            node._selected = True

    def scroll_to_line(self, line: int) -> None:
        self.scroll_to_region(Region(0, line, self.size.width, 1))

    def refresh_line(self, line: int) -> None:
        region = Region(0, line - self.scroll_offset.y, self.size.width, 1)
        self.refresh(region)

    def _refresh_node_line(self, line: int) -> None:
        node = self._get_node(line)
        if node is not None:
            self._refresh_node(node)

    def _refresh_node(self, node: TreeNode[TreeDataType]) -> None:
        """Refresh a node and all its children.

        Args:
            node (TreeNode[TreeDataType]): A tree node.
        """
        scroll_y = self.scroll_offset.y
        height = self.size.height
        visible_lines = self._tree_lines[scroll_y : scroll_y + height]
        for line_no, line in enumerate(visible_lines, scroll_y):
            if node in line.path:
                self.refresh_line(line_no)

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
            child_path = [*path, node]
            add_line(_TreeLine(child_path, last))
            if node.expanded:
                for last, child in loop_last(node.children):
                    add_node(child_path, child, last=last)

        add_node([], root, True)
        self._tree_lines_cached = lines

        width = max(lines, key=attrgetter("line_width")).line_width
        self.virtual_size = Size(width, len(lines))

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

        line = tree_lines[y]

        base_guide_style = self.get_component_rich_style("tree--guides")
        guide_hover_style = self.get_component_rich_style("tree--guides-hover")
        guide_selected_style = self.get_component_rich_style("tree--guides-selected")

        hover = self.root._hover
        selected = self.root._selected and self.has_focus

        guides = Text(style=base_style)
        guides_append = guides.append

        def get_guides(style: Style) -> tuple[str, str, str, str]:
            """Get the guide strings for a given style.

            Args:
                style (Style): A Style object.

            Returns:
                tuple[str, str, str, str]: Strings for space, vertical, terminator and cross.
            """
            lines = self.LINES["default"]
            if style.bold:
                lines = self.LINES["bold"]
            elif style.underline2:
                lines = self.LINES["double"]
            return lines

        guide_style = base_guide_style
        for node in line.path[1:]:
            if selected:
                guide_style = guide_selected_style
            if hover:
                guide_style = guide_hover_style

            space, vertical, _, _ = get_guides(guide_style)
            guide = space if node.last else vertical
            if node != line.path[-1]:
                guides_append(guide, style=guide_style)
            hover = hover or node._hover
            selected = (selected or node._selected) and self.has_focus

        if len(line.path) > 1:
            _, _, terminator, cross = get_guides(guide_style)
            if line.last:
                guides.append(terminator, style=guide_style)
            else:
                guides.append(cross, style=guide_style)
        label = line.path[-1].label.copy()
        label.stylize(self.get_component_rich_style("tree--label"))
        if self.hover_line == y:
            label.stylize(self.get_component_rich_style("tree--highlight"))
        if self.cursor_line == y and self.has_focus:
            label.stylize(self.get_component_rich_style("tree--cursor"))
        label.stylize(Style(meta={"node": line.node.id, "line": y}))

        guides.append(label)

        segments = list(guides.render(self.app.console))

        segments = line_pad(segments, 0, width - guides.cell_len, base_style)
        segments = line_crop(segments, x1, x2, width)

        return segments

    def _on_size(self) -> None:
        self.invalidate()

    def action_cursor_up(self) -> None:
        if self.cursor_line == -1:
            self.cursor_line = len(self._tree_lines)
        else:
            self.cursor_line -= 1

    def action_cursor_down(self) -> None:
        self.cursor_line += 1
