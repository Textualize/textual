import pytest

from textual.widgets import Tree
from textual.widgets.tree import TreeNode


def label_of(node: TreeNode[None]):
    """Get the label of a node as a string"""
    return str(node.label)


def test_tree_node_children() -> None:
    """A node's children property should act like an immutable list."""
    CHILDREN = 23
    tree = Tree[None]("Root")
    for child in range(CHILDREN):
        tree.root.add(str(child))
    assert len(tree.root.children) == CHILDREN
    for child in range(CHILDREN):
        assert label_of(tree.root.children[child]) == str(child)
    assert label_of(tree.root.children[0]) == "0"
    assert label_of(tree.root.children[-1]) == str(CHILDREN - 1)
    assert [label_of(node) for node in tree.root.children] == [
        str(n) for n in range(CHILDREN)
    ]
    assert [label_of(node) for node in tree.root.children[:2]] == [
        str(n) for n in range(2)
    ]
    with pytest.raises(TypeError):
        tree.root.children[0] = tree.root.children[1]
    with pytest.raises(TypeError):
        del tree.root.children[0]
    with pytest.raises(TypeError):
        del tree.root.children[0:2]
