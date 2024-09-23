from __future__ import annotations

from typing import Any

from textual import on
from textual.app import App, ComposeResult
from textual.widgets import Tree


class TreeApp(App[None]):
    """Test tree app."""

    def __init__(self, disabled: bool, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.disabled = disabled
        self.messages: list[tuple[str, str]] = []

    def compose(self) -> ComposeResult:
        """Compose the child widgets."""
        yield Tree("Root", disabled=self.disabled, id="test-tree")

    def on_mount(self) -> None:
        self.query_one(Tree).root.add("Child")
        self.query_one(Tree).focus()

    def record(
        self,
        event: (
            Tree.NodeSelected[None]
            | Tree.NodeExpanded[None]
            | Tree.NodeCollapsed[None]
            | Tree.NodeHighlighted[None]
        ),
    ) -> None:
        self.messages.append(
            (event.__class__.__name__, event.node.tree.id or "Unknown")
        )

    @on(Tree.NodeSelected)
    def node_selected(self, event: Tree.NodeSelected[None]) -> None:
        self.record(event)

    @on(Tree.NodeExpanded)
    def node_expanded(self, event: Tree.NodeExpanded[None]) -> None:
        self.record(event)

    @on(Tree.NodeCollapsed)
    def node_collapsed(self, event: Tree.NodeCollapsed[None]) -> None:
        self.record(event)

    @on(Tree.NodeHighlighted)
    def node_highlighted(self, event: Tree.NodeHighlighted[None]) -> None:
        self.record(event)


async def test_creating_disabled_tree():
    """Mounting a disabled `Tree` should result in the base `Widget`
    having a `disabled` property equal to `True`"""
    app = TreeApp(disabled=True)
    async with app.run_test() as pilot:
        tree = app.query_one(Tree)
        assert not tree.focusable
        assert tree.disabled
        assert tree.cursor_line == 0
        await pilot.click("#test-tree")
        await pilot.pause()
        await pilot.press("down")
        await pilot.pause()
        assert tree.cursor_line == 0


async def test_creating_enabled_tree():
    """Mounting an enabled `Tree` should result in the base `Widget`
    having a `disabled` property equal to `False`"""
    app = TreeApp(disabled=False)
    async with app.run_test() as pilot:
        tree = app.query_one(Tree)
        assert tree.focusable
        assert not tree.disabled
        assert tree.cursor_line == 0
        await pilot.click("#test-tree")
        await pilot.pause()
        await pilot.press("down")
        await pilot.pause()
        assert tree.cursor_line == 1


async def test_disabled_tree_node_selected_message() -> None:
    """Clicking the root node disclosure triangle on a disabled tree
    should result in no messages being emitted."""
    app = TreeApp(disabled=True)
    async with app.run_test() as pilot:
        tree = app.query_one(Tree)
        # try clicking on a disabled tree
        await pilot.click("#test-tree")
        await pilot.pause()
        assert pilot.app.messages == [("NodeHighlighted", "test-tree")]
        # make sure messages DO flow after enabling a disabled tree
        tree.disabled = False
        await pilot.click("#test-tree")
        await pilot.pause()
        print(pilot.app.messages)
        assert pilot.app.messages == [
            ("NodeHighlighted", "test-tree"),
            ("NodeExpanded", "test-tree"),
        ]


async def test_enabled_tree_node_selected_message() -> None:
    """Clicking the root node disclosure triangle on an enabled tree
    should result in an `NodeExpanded` message being emitted."""
    app = TreeApp(disabled=False)
    async with app.run_test() as pilot:
        tree = app.query_one(Tree)
        # try clicking on an enabled tree
        await pilot.click("#test-tree")
        await pilot.pause()
        print(pilot.app.messages)
        assert pilot.app.messages == [
            ("NodeHighlighted", "test-tree"),
            ("NodeExpanded", "test-tree"),
        ]
        tree.disabled = True
        # make sure messages DO NOT flow after disabling an enabled tree
        app.messages = []
        await pilot.click("#test-tree")
        await pilot.pause()
        assert not pilot.app.messages
