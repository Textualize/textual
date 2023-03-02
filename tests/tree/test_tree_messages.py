from __future__ import annotations

from typing import Any

from textual.app import App, ComposeResult
from textual.message import Message
from textual.widgets import Tree


class MyTree(Tree[None]):
    pass


class TreeApp(App[None]):
    """Test tree app."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.messages: list[str] = []

    def compose(self) -> ComposeResult:
        """Compose the child widgets."""
        yield MyTree("Root")

    def on_mount(self) -> None:
        self.query_one(MyTree).root.add("Child")
        self.query_one(MyTree).focus()

    def record(self, event: Message) -> None:
        self.messages.append(event.__class__.__name__)

    def on_tree_node_selected(self, event: Tree.NodeSelected[None]) -> None:
        self.record(event)

    def on_tree_node_expanded(self, event: Tree.NodeExpanded[None]) -> None:
        self.record(event)

    def on_tree_node_collapsed(self, event: Tree.NodeCollapsed[None]) -> None:
        self.record(event)

    def on_tree_node_highlighted(self, event: Tree.NodeHighlighted[None]) -> None:
        self.record(event)


async def test_tree_node_selected_message() -> None:
    """Selecting a node should result in a selected message being emitted."""
    async with TreeApp().run_test() as pilot:
        await pilot.press("enter")
        await pilot.pause()
        assert pilot.app.messages == ["NodeExpanded", "NodeSelected"]


async def test_tree_node_selected_message_no_auto() -> None:
    """Selecting a node should result in only a selected message being emitted."""
    async with TreeApp().run_test() as pilot:
        pilot.app.query_one(MyTree).auto_expand = False
        await pilot.press("enter")
        await pilot.pause()
        assert pilot.app.messages == ["NodeSelected"]


async def test_tree_node_expanded_message() -> None:
    """Expanding a node should result in an expanded message being emitted."""
    async with TreeApp().run_test() as pilot:
        await pilot.press("space")
        await pilot.pause()
        assert pilot.app.messages == ["NodeExpanded"]


async def test_tree_node_collapsed_message() -> None:
    """Collapsing a node should result in a collapsed message being emitted."""
    async with TreeApp().run_test() as pilot:
        await pilot.press("space", "space")
        await pilot.pause()
        assert pilot.app.messages == ["NodeExpanded", "NodeCollapsed"]


async def test_tree_node_highlighted_message() -> None:
    """Highlighting a node should result in a highlighted message being emitted."""
    async with TreeApp().run_test() as pilot:
        await pilot.press("enter", "down")
        await pilot.pause()
        assert pilot.app.messages == ["NodeExpanded", "NodeSelected", "NodeHighlighted"]
