import pytest
from rich.text import Text

from textual.widgets import Tree
from textual.widgets.tree import TreeNode


@pytest.mark.anyio
async def test_tree_node_label() -> None:
    """It should be possible to modify a TreeNode's label."""
    node = TreeNode(Tree[None]("Xenomorph Lifecycle"), None, 0, "Facehugger")
    assert node.label == Text("Facehugger")

    # posts a message so needs a running event loop
    node.label = "Chestbuster"
    assert node.label == Text("Chestbuster")


@pytest.mark.anyio
async def test_tree_node_label_via_tree() -> None:
    """It should be possible to modify a TreeNode's label when created via a Tree."""
    tree = Tree[None]("Xenomorph Lifecycle")
    node = tree.root.add("Facehugger")

    # posts a message so needs a running event loop
    assert node.label == Text("Facehugger")
    node.label = "Chestbuster"
    assert node.label == Text("Chestbuster")
