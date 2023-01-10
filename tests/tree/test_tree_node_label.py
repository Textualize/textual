from textual.widgets import Tree, TreeNode
from rich.text import Text


def test_tree_node_label() -> None:
    """It should be possible to modify a TreeNode's label."""
    node = TreeNode(Tree[None]("Xenomorph Lifecycle"), None, 0, "Facehugger")
    assert node.label == Text("Facehugger")
    node.label = "Chestbuster"
    assert node.label == Text("Chestbuster")


def test_tree_node_label_via_tree() -> None:
    """It should be possible to modify a TreeNode's label when created via a Tree."""
    tree = Tree[None]("Xenomorph Lifecycle")
    node = tree.root.add("Facehugger")
    assert node.label == Text("Facehugger")
    node.label = "Chestbuster"
    assert node.label == Text("Chestbuster")
