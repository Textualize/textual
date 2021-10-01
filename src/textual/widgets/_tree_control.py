from __future__ import annotations


from typing import Generic, Iterator, NewType, TypeVar

import rich.repr
from rich.console import RenderableType
from rich.text import Text, TextType
from rich.tree import Tree
from rich.padding import PaddingDimensions

from .. import log
from .. import events
from ..reactive import Reactive
from .._types import MessageTarget
from ..widget import Widget
from ..message import Message
from ..messages import CursorMove


NodeID = NewType("NodeID", int)


NodeDataType = TypeVar("NodeDataType")


@rich.repr.auto
class TreeNode(Generic[NodeDataType]):
    def __init__(
        self,
        parent: TreeNode[NodeDataType] | None,
        node_id: NodeID,
        control: TreeControl,
        tree: Tree,
        label: TextType,
        data: NodeDataType,
    ) -> None:
        self.parent = parent
        self.id = node_id
        self._control = control
        self._tree = tree
        self.label = label
        self.data = data
        self.loaded = False
        self._expanded = False
        self._empty = False
        self._tree.expanded = False
        self.children: list[TreeNode] = []

    def __rich_repr__(self) -> rich.repr.Result:
        yield "id", self.id
        yield "label", self.label
        yield "data", self.data

    @property
    def control(self) -> TreeControl:
        return self._control

    @property
    def empty(self) -> bool:
        return self._empty

    @property
    def expanded(self) -> bool:
        return self._expanded

    @property
    def is_cursor(self) -> bool:
        return self.control.cursor == self.id and self.control.show_cursor

    @property
    def tree(self) -> Tree:
        return self._tree

    @property
    def next_node(self) -> TreeNode[NodeDataType] | None:
        """The next node in the tree, or None if at the end."""

        if self.expanded and self.children:
            return self.children[0]
        else:

            sibling = self.next_sibling
            if sibling is not None:
                return sibling

            node = self
            while True:
                if node.parent is None:
                    return None
                sibling = node.parent.next_sibling
                if sibling is not None:
                    return sibling
                else:
                    node = node.parent

    @property
    def previous_node(self) -> TreeNode[NodeDataType] | None:
        """The previous node in the tree, or None if at the end."""

        sibling = self.previous_sibling
        if sibling is not None:

            def last_sibling(node) -> TreeNode[NodeDataType]:
                if node.expanded and node.children:
                    return last_sibling(node.children[-1])
                else:
                    return (
                        node.children[-1] if (node.children and node.expanded) else node
                    )

            return last_sibling(sibling)

        if self.parent is None:
            return None
        return self.parent

    @property
    def next_sibling(self) -> TreeNode[NodeDataType] | None:
        """The next sibling, or None if last sibling."""
        if self.parent is None:
            return None
        iter_siblings = iter(self.parent.children)
        try:
            for node in iter_siblings:
                if node is self:
                    return next(iter_siblings)
        except StopIteration:
            pass
        return None

    @property
    def previous_sibling(self) -> TreeNode[NodeDataType] | None:
        """Previous sibling or None if first sibling."""
        if self.parent is None:
            return None
        iter_siblings = iter(self.parent.children)
        sibling: TreeNode[NodeDataType] | None = None

        for node in iter_siblings:
            if node is self:
                return sibling
            sibling = node
        return None

    async def expand(self, expanded: bool = True) -> None:
        self._expanded = expanded
        self._tree.expanded = expanded
        self._control.refresh(layout=True)

    async def toggle(self) -> None:
        await self.expand(not self._expanded)

    async def add(self, label: TextType, data: NodeDataType) -> None:
        await self._control.add(self.id, label, data=data)
        self._control.refresh(layout=True)
        self._empty = False

    def __rich__(self) -> RenderableType:
        return self._control.render_node(self)


@rich.repr.auto
class TreeClick(Generic[NodeDataType], Message, bubble=True):
    def __init__(self, sender: MessageTarget, node: TreeNode[NodeDataType]) -> None:
        self.node = node
        super().__init__(sender)

    def __rich_repr__(self) -> rich.repr.Result:
        yield "node", self.node


class TreeControl(Generic[NodeDataType], Widget):
    def __init__(
        self,
        label: TextType,
        data: NodeDataType,
        *,
        name: str | None = None,
        padding: PaddingDimensions = (1, 1),
    ) -> None:
        self.data = data

        self.id = NodeID(0)
        self.nodes: dict[NodeID, TreeNode[NodeDataType]] = {}
        self._tree = Tree(label)
        self.root: TreeNode[NodeDataType] = TreeNode(
            None, self.id, self, self._tree, label, data
        )

        self._tree.label = self.root
        self.nodes[NodeID(self.id)] = self.root
        super().__init__(name=name)
        self.padding = padding

    hover_node: Reactive[NodeID | None] = Reactive(None)
    cursor: Reactive[NodeID] = Reactive(NodeID(0), layout=True)
    cursor_line: Reactive[int] = Reactive(0, repaint=False)
    show_cursor: Reactive[bool] = Reactive(False, layout=True)

    def watch_show_cursor(self, value: bool) -> None:
        self.emit_no_wait(CursorMove(self, self.cursor_line))

    def watch_cursor_line(self, value: int) -> None:
        if self.show_cursor:
            self.emit_no_wait(CursorMove(self, value + self.gutter.top))

    async def add(
        self,
        node_id: NodeID,
        label: TextType,
        data: NodeDataType,
    ) -> None:
        parent = self.nodes[node_id]
        self.id = NodeID(self.id + 1)
        child_tree = parent._tree.add(label)
        child_node: TreeNode[NodeDataType] = TreeNode(
            parent, self.id, self, child_tree, label, data
        )
        parent.children.append(child_node)
        child_tree.label = child_node
        self.nodes[self.id] = child_node

        self.refresh(layout=True)

    def find_cursor(self) -> int | None:
        """Find the line location for the cursor node."""

        node_id = self.cursor
        line = 0

        stack: list[Iterator[TreeNode[NodeDataType]]]
        stack = [iter([self.root])]

        pop = stack.pop
        push = stack.append
        while stack:
            iter_children = pop()
            try:
                node = next(iter_children)
            except StopIteration:
                continue
            else:
                if node.id == node_id:
                    return line
                line += 1
                push(iter_children)
                if node.children and node.expanded:
                    push(iter(node.children))
        return None

    def render(self) -> RenderableType:
        return self._tree

    def render_node(self, node: TreeNode[NodeDataType]) -> RenderableType:
        label = (
            Text(node.label, no_wrap=True, overflow="ellipsis")
            if isinstance(node.label, str)
            else node.label
        )
        if node.id == self.hover_node:
            label.stylize("underline")
        label.apply_meta({"@click": f"click_label({node.id})", "tree_node": node.id})
        return label

    async def action_click_label(self, node_id: NodeID) -> None:
        node = self.nodes[node_id]
        self.cursor = node.id
        self.cursor_line = self.find_cursor() or 0
        self.show_cursor = False
        await self.post_message(TreeClick(self, node))

    async def on_mouse_move(self, event: events.MouseMove) -> None:
        self.hover_node = event.style.meta.get("tree_node")

    async def on_key(self, event: events.Key) -> None:
        await self.dispatch_key(event)

    async def key_down(self, event: events.Key) -> None:
        event.stop()
        await self.cursor_down()

    async def key_up(self, event: events.Key) -> None:
        event.stop()
        await self.cursor_up()

    async def key_enter(self, event: events.Key) -> None:
        cursor_node = self.nodes[self.cursor]
        event.stop()
        await self.post_message(TreeClick(self, cursor_node))

    async def cursor_down(self) -> None:
        if not self.show_cursor:
            self.show_cursor = True
            return
        cursor_node = self.nodes[self.cursor]
        next_node = cursor_node.next_node
        if next_node is not None:
            self.cursor_line += 1
            self.cursor = next_node.id

    async def cursor_up(self) -> None:
        if not self.show_cursor:
            self.show_cursor = True
            return
        cursor_node = self.nodes[self.cursor]
        previous_node = cursor_node.previous_node
        if previous_node is not None:
            self.cursor_line -= 1
            self.cursor = previous_node.id


if __name__ == "__main__":

    from textual import events
    from textual.app import App

    class TreeApp(App):
        async def on_mount(self, event: events.Mount) -> None:
            await self.view.dock(TreeControl("Tree Root", data="foo"))

        async def handle_tree_click(self, message: TreeClick) -> None:
            if message.node.empty:
                await message.node.add("foo")
                await message.node.add("bar")
                await message.node.add("baz")
                await message.node.expand()
            else:
                await message.node.toggle()

    TreeApp.run(log="textual.log")
