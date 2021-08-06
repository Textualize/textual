from __future__ import annotations

from typing import Any, Generic, NewType, TypeVar

from rich.console import Console, ConsoleOptions, RenderableType

from rich.style import Style, StyleType
from rich.styled import Styled
from rich.text import Text, TextType
from rich.tree import Tree
from rich.padding import Padding, PaddingDimensions

from .. import log
from ..reactive import Reactive
from .._types import MessageTarget
from ..widget import Widget
from ..message import Message


NodeID = NewType("NodeID", int)


NodeDataType = TypeVar("NodeDataType")


class TreeNode(Generic[NodeDataType]):
    def __init__(
        self,
        node_id: NodeID,
        control: TreeControl,
        tree: Tree,
        label: TextType,
        data: NodeDataType,
    ) -> None:
        self._node_id = node_id
        self._control = control
        self._tree = tree
        self.label = label
        self.data = data
        self.loaded = False
        self._expanded = False
        self._empty = False
        self._tree.expanded = False

    @property
    def id(self) -> NodeID:
        return self._node_id

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
    def tree(self) -> Tree:
        return self._tree

    async def expand(self, expanded: bool = True) -> None:
        self._expanded = expanded
        self._tree.expanded = expanded
        self._control.refresh()

    async def toggle(self) -> None:
        await self.expand(not self._expanded)

    async def add(self, label: TextType, data: NodeDataType) -> None:
        await self._control.add(self._node_id, label, data=data)
        self._control.refresh()
        self._empty = False

    def __rich__(self) -> RenderableType:
        return self._control.render_node(self)


class TreeClick(Generic[NodeDataType], Message, bubble=True):
    def __init__(self, sender: MessageTarget, node: TreeNode[NodeDataType]) -> None:
        self.node = node
        super().__init__(sender)


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

        self._node_id = NodeID(0)
        self.nodes: dict[NodeID, TreeNode[NodeDataType]] = {}
        self._tree = Tree(label)
        self.root: TreeNode[NodeDataType] = TreeNode(
            self._node_id, self, self._tree, label, data
        )
        self._tree.label = self.root
        self.nodes[NodeID(self._node_id)] = self.root
        self.padding = padding
        super().__init__(name=name)

    hover_node: Reactive[NodeID | None] = Reactive(None)

    async def add(
        self,
        node_id: NodeID,
        label: TextType,
        data: NodeDataType,
    ) -> None:
        parent = self.nodes[node_id]
        self._node_id = NodeID(self._node_id + 1)
        child_tree = parent._tree.add(label)
        child_node: TreeNode[NodeDataType] = TreeNode(
            self._node_id, self, child_tree, label, data
        )
        child_tree.label = child_node
        self.nodes[self._node_id] = child_node

        self.refresh()

    def render(self) -> RenderableType:
        return Padding(self._tree, self.padding)

    def render_node(self, node: TreeNode[NodeDataType]) -> RenderableType:
        meta = {"@click": f"click_label({node.id})", "tree_node": node.id}
        label = Text(node.label) if isinstance(node.label, str) else node.label
        if node.id == self.hover_node:
            label.stylize("underline")
        label.apply_meta(meta)
        label.no_wrap = True
        label.overflow = "ellipsis"
        return label

    async def action_click_label(self, node_id: NodeID) -> None:
        node = self.nodes[node_id]
        await self.post_message(TreeClick(self, node))

    async def on_mouse_move(self, event: events.MouseMove) -> None:
        self.hover_node = event.style.meta.get("tree_node")


if __name__ == "__main__":

    from textual import events
    from textual.app import App

    class TreeApp(App):
        async def on_mount(self, event: events.Mount) -> None:
            await self.view.dock(TreeControl("Tree Root", data="foo"))

        async def message_tree_click(self, message: TreeClick) -> None:
            if message.node.empty:
                await message.node.add("foo")
                await message.node.add("bar")
                await message.node.add("baz")
                await message.node.expand()
            else:
                await message.node.toggle()

    TreeApp.run(log="textual.log")
