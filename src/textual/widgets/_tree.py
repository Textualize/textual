from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, ClassVar, Generic, NewType, TypeVar

import rich.repr
from rich.segment import Segment
from rich.style import Style
from rich.text import Text, TextType


from ..binding import Binding
from ..geometry import clamp, Region, Size
from .._loop import loop_last
from .._cache import LRUCache
from ..message import Message
from ..reactive import reactive, var
from .._segment_tools import line_crop, line_pad
from .._types import MessageTarget
from .._typing import TypeAlias
from ..scroll_view import ScrollView

from .. import events

NodeID = NewType("NodeID", int)
TreeDataType = TypeVar("TreeDataType")
EventTreeDataType = TypeVar("EventTreeDataType")

LineCacheKey: TypeAlias = tuple[int | tuple[int, ...], ...]


@dataclass
class _TreeLine:
    path: list[TreeNode]
    last: bool

    @property
    def node(self) -> TreeNode:
        return self.path[-1]

    def get_line_width(self, guide_depth: int) -> int:
        return (len(self.path)) + self.path[-1]._label.cell_len - guide_depth


@rich.repr.auto
class TreeNode(Generic[TreeDataType]):
    def __init__(
        self,
        tree: Tree[TreeDataType],
        parent: TreeNode[TreeDataType] | None,
        id: NodeID,
        label: Text,
        data: TreeDataType | None = None,
        *,
        expanded: bool = True,
        allow_expand: bool = True,
    ) -> None:
        self._tree = tree
        self._parent = parent
        self._id = id
        self._label = label
        self.data: TreeDataType = data if data is not None else tree._data_factory()
        self._expanded = expanded
        self._children: list[TreeNode] = []

        self._hover = False
        self._selected = False
        self._allow_expand = allow_expand
        self._updates: int = 0

    def __rich_repr__(self) -> rich.repr.Result:
        yield self._label.plain
        yield self.data

    def _reset(self) -> None:
        self._hover = False
        self._selected = False
        self._updates += 1

    @property
    def hover(self) -> bool:
        return self._hover

    @hover.setter
    def hover(self, hover: bool) -> None:
        self._updates += 1
        self._hover = hover

    @property
    def selected(self) -> bool:
        return self._selected

    @hover.setter
    def selected(self, selected: bool) -> None:
        self._updates += 1
        self._selected = selected

    @property
    def id(self) -> NodeID:
        """Get the node ID."""
        return self._id

    def expand(self) -> None:
        """Expand a node (show its children)."""
        self._expanded = True
        self._updates += 1
        self._tree._invalidate()

    def collapse(self) -> None:
        """Collapse the node (hide children)."""
        self._expanded = False
        self._updates += 1
        self._tree._invalidate()

    def toggle(self) -> None:
        """Toggle the expanded state."""
        self._expanded = not self._expanded
        self._updates += 1
        self._tree._invalidate()

    def set_label(self, label: TextType) -> None:
        """Set a new label for the node.

        Args:
            label (TextType): A str or Text object with the new label.
        """
        self._updates += 1
        text_label = self._tree.process_label(label)
        self._label = text_label
        self._tree._invalidate()

    @property
    def is_expanded(self) -> bool:
        """Check if the node is expanded."""
        return self._expanded

    @property
    def last(self) -> bool:
        """Check if this is the last child.

        Returns:
            bool: True if this is the last child, otherwise False.
        """
        if self._parent is None:
            return True
        return bool(
            self._parent._children and self._parent._children[-1] == self,
        )

    def add(
        self,
        label: TextType,
        data: TreeDataType | None = None,
        *,
        expand: bool = False,
        allow_expand: bool = True,
    ) -> TreeNode[TreeDataType]:
        """Add a node to the sub-tree.

        Args:
            label (TextType): The new node's label.
            data (TreeDataType): Data associated with the new node.
            expanded (bool, optional): Node should be expanded. Defaults to True.

        Returns:
            TreeNode[TreeDataType]: A new Tree node
        """
        if isinstance(label, str):
            text_label = Text.from_markup(label)
        else:
            text_label = label
        node = self._tree._add_node(self, text_label, data)
        node._expanded = expand
        node._allow_expand = allow_expand
        self._updates += 1
        self._children.append(node)
        self._tree._invalidate()
        return node


class Tree(Generic[TreeDataType], ScrollView, can_focus=True):

    BINDINGS = [
        Binding("up", "cursor_up", "Cursor Up", show=False),
        Binding("down", "cursor_down", "Cursor Down", show=False),
        Binding("enter", "select_cursor", "Select", show=False),
    ]

    DEFAULT_CSS = """
    Tree {
        background: $panel;
        color: $text;
    }
    Tree > .tree--label {
        
    }
    Tree > .tree--guides {
        color: $success-darken-3;
    }

    Tree > .tree--guides-hover {  
        color: $success;      
        text-style: bold;
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
    
    Tree > .tree--highlight-line {        
        background: $boost;
    }

    """

    COMPONENT_CLASSES: ClassVar[set[str]] = {
        "tree--label",
        "tree--guides",
        "tree--guides-hover",
        "tree--guides-selected",
        "tree--cursor",
        "tree--highlight",
        "tree--highlight-line",
    }

    show_root = reactive(True)
    hover_line = var(-1)
    cursor_line = var(-1)
    show_guides = reactive(True)
    guide_depth = reactive(4, init=False)
    auto_expand = var(True)

    LINES: dict[str, tuple[str, str, str, str]] = {
        "default": (
            "  ",
            "│ ",
            "└─",
            "├─",
        ),
        "bold": (
            "  ",
            "┃ ",
            "┗━",
            "┣━",
        ),
        "double": (
            "  ",
            "║ ",
            "╚═",
            "╠═",
        ),
    }

    class NodeSelected(Generic[EventTreeDataType], Message, bubble=True):
        def __init__(
            self, sender: MessageTarget, node: TreeNode[EventTreeDataType]
        ) -> None:
            self.node = node
            super().__init__(sender)

    def __init__(
        self,
        label: TextType,
        data: TreeDataType | None = None,
        data_factory: Callable[[], TreeDataType] = dict,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)

        text_label = self.process_label(label)

        self._data_factory = data_factory
        self._updates = 0
        self._nodes: dict[NodeID, TreeNode[TreeDataType]] = {}
        self._current_id = 0
        self.root = self._add_node(None, text_label, data)

        self._line_cache: LRUCache[LineCacheKey, list[Segment]] = LRUCache(1024)
        self._tree_lines_cached: list[_TreeLine] | None = None

    @classmethod
    def process_label(cls, label: TextType):
        """Process a str or Text in to a label. Maybe overridden in a subclass to change modify how labels are rendered.

        Args:
            label (TextType): Label.

        Returns:
            Text: A Rich Text object.
        """
        if isinstance(label, str):
            text_label = Text.from_markup(label)
        else:
            text_label = label
        first_line = text_label.split()[0]
        return first_line

    def _add_node(
        self,
        parent: TreeNode[TreeDataType] | None,
        label: Text,
        data: TreeDataType | None,
        expand: bool = False,
    ) -> TreeNode[TreeDataType]:
        node_data = data if data is not None else self._data_factory()
        node = TreeNode(self, parent, self._new_id(), label, node_data, expanded=expand)
        self._nodes[node._id] = node
        self._updates += 1
        return node

    def render_label(
        self, node: TreeNode[TreeDataType], base_style: Style, style: Style
    ) -> Text:
        """Render a label for the given node. Override this to modify how labels are rendered.

        Args:
            node (TreeNode[TreeDataType]): A tree node.

        Returns:
            Text: A Rich Text object containing the label.
        """
        node_label = node._label.copy()
        node_label.stylize(style)

        if node._allow_expand:
            prefix = (
                "▼ " if node.is_expanded else "▶ ",
                base_style + Style.from_meta({"toggle": True}),
            )
        else:
            prefix = ("", base_style)

        text = Text.assemble(prefix, node_label)
        return text

    def clear(self) -> None:
        """Clear all nodes under root."""
        self._tree_lines_cached = None
        self._current_id = 0
        root_label = self.root._label
        root_data = self.root.data
        self.root = TreeNode(
            self,
            None,
            self._new_id(),
            root_label,
            root_data,
            expanded=True,
        )
        self._updates += 1
        self.refresh()

    def get_node_at_line(self, line_no: int) -> TreeNode[TreeDataType] | None:
        """Get the node for a given line.

        Args:
            line_no (int): A line number.

        Returns:
            TreeNode[TreeDataType] | None: A tree node, or ``None`` if there is no node at that line.
        """
        try:
            line = self._tree_lines[line_no]
        except IndexError:
            return None
        else:
            return line.node

    def add_json(self, node: TreeNode, json_data: object) -> None:

        from rich.highlighter import ReprHighlighter

        highlighter = ReprHighlighter()

        def add_node(name: str, node: TreeNode, data: object) -> None:
            if isinstance(data, dict):
                node._label = Text(f"{{}} {name}")
                for key, value in data.items():
                    new_node = node.add("")
                    add_node(key, new_node, value)
            elif isinstance(data, list):
                node._label = Text(f"[] {name}")
                for index, value in enumerate(data):
                    new_node = node.add("")
                    add_node(str(index), new_node, value)
            else:
                node._allow_expand = False
                if name:
                    label = Text.assemble(
                        Text.from_markup(f"[b]{name}[/b]="), highlighter(repr(data))
                    )
                else:
                    label = Text(repr(data))
                node._label = label

        add_node("JSON", node, json_data)
        self._invalidate()

    def validate_cursor_line(self, value: int) -> int:
        return clamp(value, 0, len(self._tree_lines) - 1)

    def validate_guide_depth(self, value: int) -> int:
        return clamp(value, 2, 10)

    def _invalidate(self) -> None:
        """Invalidate caches."""
        self._line_cache.clear()
        self._tree_lines_cached = None
        self._updates += 1
        self.root._reset()
        self.refresh(layout=True)

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
            previous_node.hover = False

        node = self._get_node(hover_line)
        if node is not None:
            self._refresh_node(node)
            node.hover = True

    def watch_cursor_line(self, previous_line: int, line: int) -> None:
        previous_node = self._get_node(previous_line)
        if previous_node is not None:
            self._refresh_node(previous_node)
            previous_node.selected = False

        node = self._get_node(line)
        if node is not None:
            self._refresh_node(node)
            self.scroll_to_line(line)
            node.selected = True

    def watch_guide_depth(self, guide_depth: int) -> None:
        self._invalidate()

    def watch_show_root(self, show_root: bool) -> None:
        self._invalidate()

    def scroll_to_line(self, line: int) -> None:
        """Scroll to the given line.

        Args:
            line (int): A line number.
        """
        self.scroll_to_region(Region(0, line, self.size.width, 1))

    def refresh_line(self, line: int) -> None:
        """Refresh (repaint) a given line in the tree.

        Args:
            line (int): Line number.
        """
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
            if node._expanded:
                for last, child in loop_last(node._children):
                    add_node(child_path, child, last=last)

        if self.show_root:
            add_node([], root, True)
        else:
            for node in self.root._children:
                add_node([], node, True)
        self._tree_lines_cached = lines

        guide_depth = self.guide_depth
        if lines:
            width = max([line.get_line_width(guide_depth) for line in lines])
        else:
            width = self.size.width

        self.virtual_size = Size(width, len(lines))
        if self.cursor_line >= len(lines):
            self.cursor_line = -1

    def render_line(self, y: int) -> list[Segment]:
        width = self.size.width
        scroll_x, scroll_y = self.scroll_offset
        style = self.rich_style
        return self._render_line(
            y + scroll_y,
            scroll_x,
            scroll_x + width,
            style,
        )

    def _render_line(
        self, y: int, x1: int, x2: int, base_style: Style
    ) -> list[Segment]:
        tree_lines = self._tree_lines
        width = self.size.width

        if y >= len(tree_lines):
            return [Segment(" " * width, base_style)]

        line = tree_lines[y]

        is_hover = self.hover_line >= 0 and any(node._hover for node in line.path)

        cache_key = (
            y,
            is_hover,
            width,
            self._updates,
            y == self.hover_line,
            y == self.cursor_line,
            self.has_focus,
            tuple(node._updates for node in line.path),
        )
        if cache_key in self._line_cache:
            segments = self._line_cache[cache_key]
        else:
            base_guide_style = self.get_component_rich_style(
                "tree--guides", partial=True
            )
            guide_hover_style = base_guide_style + self.get_component_rich_style(
                "tree--guides-hover", partial=True
            )
            guide_selected_style = base_guide_style + self.get_component_rich_style(
                "tree--guides-selected", partial=True
            )

            hover = self.root._hover
            selected = self.root._selected and self.has_focus

            def get_guides(style: Style) -> tuple[str, str, str, str]:
                """Get the guide strings for a given style.

                Args:
                    style (Style): A Style object.

                Returns:
                    tuple[str, str, str, str]: Strings for space, vertical, terminator and cross.
                """
                if self.show_guides:
                    lines = self.LINES["default"]
                    if style.bold:
                        lines = self.LINES["bold"]
                    elif style.underline2:
                        lines = self.LINES["double"]
                else:
                    lines = ("  ", "  ", "  ", "  ")

                guide_depth = max(0, self.guide_depth - 2)
                lines = tuple(
                    f"{vertical}{horizontal * guide_depth} "
                    for vertical, horizontal in lines
                )
                return lines

            if is_hover:
                line_style = self.get_component_rich_style("tree--highlight-line")
            else:
                line_style = base_style

            guides = Text(style=line_style)
            guides_append = guides.append

            guide_style = base_guide_style
            for node in line.path[1:]:
                if hover:
                    guide_style = guide_hover_style
                if selected:
                    guide_style = guide_selected_style

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

            label_style = self.get_component_rich_style("tree--label", partial=True)
            if self.hover_line == y:
                label_style += self.get_component_rich_style(
                    "tree--highlight", partial=True
                )
            if self.cursor_line == y and self.has_focus:
                label_style += self.get_component_rich_style(
                    "tree--cursor", partial=False
                )

            label = self.render_label(line.path[-1], line_style, label_style).copy()
            label.stylize(Style(meta={"node": line.node._id, "line": y}))
            guides.append(label)

            segments = list(guides.render(self.app.console))
            pad_width = max(self.virtual_size.width, width)
            segments = line_pad(segments, 0, pad_width - guides.cell_len, line_style)
            self._line_cache[cache_key] = segments

        segments = line_crop(segments, x1, x2, width)

        return segments

    def _on_resize(self, event: events.Resize) -> None:
        self._line_cache.grow(event.size.height)
        self._invalidate()

    async def _on_click(self, event: events.Click) -> None:
        meta = event.style.meta
        if "line" in meta:
            cursor_line = meta["line"]
            if meta.get("toggle", False):
                node = self.get_node_at_line(cursor_line)
                if node is not None:
                    node.toggle()
            else:
                if self.cursor_line == cursor_line:
                    await self.action("select_cursor")
                else:
                    self.cursor_line = cursor_line

    def action_cursor_up(self) -> None:
        if self.cursor_line == -1:
            self.cursor_line = len(self._tree_lines) - 1
        else:
            self.cursor_line -= 1

    def action_cursor_down(self) -> None:
        self.cursor_line += 1

    def action_select_cursor(self) -> None:
        try:
            line = self._tree_lines[self.cursor_line]
        except IndexError:
            pass
        else:
            node = line.path[-1]
            if self.auto_expand:
                node.toggle()
            self.emit_no_wait(self.NodeSelected(self, line.path[-1]))
