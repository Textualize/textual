from __future__ import annotations

from typing import Any

from textual import on
from textual.app import App, ComposeResult
from textual.widgets import Tree
from textual.widgets.tree import NodeID, TreeNode


class TreeApp(App[None]):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.messages: list[tuple[str, NodeID]] = []

    def compose(self) -> ComposeResult:
        tree = Tree[str](label="tree")
        self._node = tree.root.add_leaf("leaf")
        tree.root.expand()
        yield tree

    @property
    def node(self) -> TreeNode[str]:
        return self._node

    @on(Tree.NodeHighlighted)
    @on(Tree.NodeSelected)
    @on(Tree.NodeCollapsed)
    @on(Tree.NodeExpanded)
    def record_event(
        self,
        event: (
            Tree.NodeHighlighted[str]
            | Tree.NodeSelected[str]
            | Tree.NodeCollapsed[str]
            | Tree.NodeExpanded[str]
        ),
    ) -> None:
        self.messages.append((event.__class__.__name__, event.node.id))


async def test_move_cursor() -> None:
    """Test moving the cursor to a node (updating the highlighted node)."""
    async with TreeApp().run_test() as pilot:
        app = pilot.app
        tree: Tree[str] = app.query_one(Tree)
        node_to_move_to = app.node
        tree.move_cursor(node_to_move_to)
        await pilot.pause()

        # Note there are no Selected messages. We only move the cursor.
        assert app.messages == [
            ("NodeExpanded", 0),  # From the call to `tree.root.expand()` in compose
            ("NodeHighlighted", 0),  # From the initial highlight of the root node
            ("NodeHighlighted", 1),  # From the call to `tree.move_cursor`
        ]


async def test_move_cursor_reset() -> None:
    async with TreeApp().run_test() as pilot:
        app = pilot.app
        tree: Tree[str] = app.query_one(Tree)
        tree.move_cursor(app.node)
        tree.move_cursor(None)
        await pilot.pause()
        assert app.messages == [
            ("NodeExpanded", 0),  # From the call to `tree.root.expand()` in compose
            ("NodeHighlighted", 0),  # From the initial highlight of the root node
            ("NodeHighlighted", 1),  # From the 1st call to `tree.move_cursor`
            ("NodeHighlighted", 0),  # From the call to `tree.move_cursor(None)`
        ]


async def test_select_node() -> None:
    async with TreeApp().run_test() as pilot:
        app = pilot.app
        tree: Tree[str] = app.query_one(Tree)
        tree.select_node(app.node)
        await pilot.pause()
        assert app.messages == [
            ("NodeExpanded", 0),  # From the call to `tree.root.expand()` in compose
            ("NodeHighlighted", 0),  # From the initial highlight of the root node
            ("NodeHighlighted", 1),  # From the `tree.select_node` call
            ("NodeSelected", 1),  # From the call to `tree.select_node`
        ]


async def test_select_node_reset() -> None:
    async with TreeApp().run_test() as pilot:
        app = pilot.app
        tree: Tree[str] = app.query_one(Tree)
        tree.move_cursor(app.node)
        tree.select_node(None)
        await pilot.pause()

        # Notice no Selected messages.
        assert app.messages == [
            ("NodeExpanded", 0),  # From the call to `tree.root.expand()` in compose
            ("NodeHighlighted", 0),  # From the initial highlight of the root node
            ("NodeHighlighted", 1),  # From the `tree.move_cursor` call
            ("NodeHighlighted", 0),  # From the call to `tree.select_node(None)`
        ]
