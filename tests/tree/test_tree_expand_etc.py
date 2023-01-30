from __future__ import annotations

from textual.app import App, ComposeResult
from textual.widgets import Tree


class TreeApp(App[None]):
    """Test tree app."""

    def compose(self) -> ComposeResult:
        yield Tree("Test")

    def on_mount(self) -> None:
        tree = self.query_one(Tree)
        for n in range(10):
            tree.root.add(f"Trunk {n}")
        node = tree.root.children[0]
        for n in range(10):
            node = node.add(str(n))


async def test_tree_node_expand() -> None:
    """Expanding one node should not expand all nodes."""
    async with TreeApp().run_test() as pilot:
        pilot.app.query_one(Tree).root.expand()
        assert pilot.app.query_one(Tree).root.is_expanded is True
        check_node = pilot.app.query_one(Tree).root.children[0]
        while check_node.children:
            assert any(child.is_expanded for child in check_node.children) is False
            check_node = check_node.children[0]


async def test_tree_node_expand_all() -> None:
    """Expanding all on a node should expand all child nodes too."""
    async with TreeApp().run_test() as pilot:
        pilot.app.query_one(Tree).root.expand_all()
        assert pilot.app.query_one(Tree).root.is_expanded is True
        check_node = pilot.app.query_one(Tree).root.children[0]
        while check_node.children:
            assert check_node.children[0].is_expanded is True
            assert any(child.is_expanded for child in check_node.children[1:]) is False
            check_node = check_node.children[0]


async def test_tree_node_collapse() -> None:
    """Collapsing one node should not collapse all nodes."""
    async with TreeApp().run_test() as pilot:
        pilot.app.query_one(Tree).root.expand_all()
        pilot.app.query_one(Tree).root.children[0].collapse()
        assert pilot.app.query_one(Tree).root.children[0].is_expanded is False
        check_node = pilot.app.query_one(Tree).root.children[0].children[0]
        while check_node.children:
            assert all(child.is_expanded for child in check_node.children) is True
            check_node = check_node.children[0]


async def test_tree_node_collapse_all() -> None:
    """Collapsing all on a node should collapse all child noes too."""
    async with TreeApp().run_test() as pilot:
        pilot.app.query_one(Tree).root.expand_all()
        pilot.app.query_one(Tree).root.children[0].collapse_all()
        assert pilot.app.query_one(Tree).root.children[0].is_expanded is False
        check_node = pilot.app.query_one(Tree).root.children[0].children[0]
        while check_node.children:
            assert check_node.children[0].is_expanded is False
            assert all(child.is_expanded for child in check_node.children[1:]) is True
            check_node = check_node.children[0]


async def test_tree_node_toggle() -> None:
    """Toggling one node should not toggle all nodes."""
    async with TreeApp().run_test() as pilot:
        assert pilot.app.query_one(Tree).root.is_expanded is False
        check_node = pilot.app.query_one(Tree).root.children[0]
        while check_node.children:
            assert any(child.is_expanded for child in check_node.children) is False
            check_node = check_node.children[0]
        pilot.app.query_one(Tree).root.toggle()
        assert pilot.app.query_one(Tree).root.is_expanded is True
        check_node = pilot.app.query_one(Tree).root.children[0]
        while check_node.children:
            assert any(child.is_expanded for child in check_node.children) is False
            check_node = check_node.children[0]


async def test_tree_node_toggle_all() -> None:
    """Toggling all on a node should toggle all child nodes too."""
    async with TreeApp().run_test() as pilot:
        assert pilot.app.query_one(Tree).root.is_expanded is False
        check_node = pilot.app.query_one(Tree).root.children[0]
        while check_node.children:
            assert any(child.is_expanded for child in check_node.children) is False
            check_node = check_node.children[0]
        pilot.app.query_one(Tree).root.toggle_all()
        assert pilot.app.query_one(Tree).root.is_expanded is True
        check_node = pilot.app.query_one(Tree).root.children[0]
        while check_node.children:
            assert check_node.children[0].is_expanded is True
            assert any(child.is_expanded for child in check_node.children[1:]) is False
            check_node = check_node.children[0]
        pilot.app.query_one(Tree).root.toggle_all()
        assert pilot.app.query_one(Tree).root.is_expanded is False
        check_node = pilot.app.query_one(Tree).root.children[0]
        while check_node.children:
            assert any(child.is_expanded for child in check_node.children) is False
            check_node = check_node.children[0]
