import pytest

from textual.widgets import Tree
from textual.widgets.tree import AddNodeError


def test_tree_node_add_before_and_after_raises_exception():
    tree = Tree[None]("root")
    with pytest.raises(AddNodeError):
        tree.root.add("error", before=99, after=0)


def test_tree_node_add_before_index():
    tree = Tree[None]("root")
    tree.root.add("node")
    tree.root.add("before node", before=0)
    tree.root.add("first", before=-99)
    tree.root.add("after first", before=-2)
    tree.root.add("last", before=99)
    tree.root.add("after node", before=4)
    tree.root.add("before last", before=-1)

    assert str(tree.root.children[0].label) == "first"
    assert str(tree.root.children[1].label) == "after first"
    assert str(tree.root.children[2].label) == "before node"
    assert str(tree.root.children[3].label) == "node"
    assert str(tree.root.children[4].label) == "after node"
    assert str(tree.root.children[5].label) == "before last"
    assert str(tree.root.children[6].label) == "last"


def test_tree_node_add_after_index():
    tree = Tree[None]("root")
    tree.root.add("node")
    tree.root.add("after node", after=0)
    tree.root.add("first", after=-99)
    tree.root.add("after first", after=-3)
    tree.root.add("before node", after=1)
    tree.root.add("before last", after=99)
    tree.root.add("last", after=-1)

    assert str(tree.root.children[0].label) == "first"
    assert str(tree.root.children[1].label) == "after first"
    assert str(tree.root.children[2].label) == "before node"
    assert str(tree.root.children[3].label) == "node"
    assert str(tree.root.children[4].label) == "after node"
    assert str(tree.root.children[5].label) == "before last"
    assert str(tree.root.children[6].label) == "last"
