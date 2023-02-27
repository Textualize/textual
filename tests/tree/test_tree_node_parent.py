from textual.widgets import Tree


def test_tree_node_parent() -> None:
    """It should be possible to access a TreeNode's parent."""
    tree = Tree[None]("Anakin")
    child = tree.root.add("Leia")
    grandchild = child.add("Ben")
    assert tree.root.parent is None
    assert grandchild.parent == child
    assert child.parent == tree.root
