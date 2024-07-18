import pytest

from textual.widgets import Tree
from textual.widgets.tree import AddNodeError


def test_tree_node_add_before_and_after_raises_exception():
    tree = Tree[None]("root")
    with pytest.raises(AddNodeError):
        tree.root.add("error", before=99, after=0)


def test_tree_node_add_before_or_after_with_invalid_type_raises_exception():
    tree = Tree[None]("root")
    tree.root.add("node")
    with pytest.raises(TypeError):
        tree.root.add("before node", before="node")
    with pytest.raises(TypeError):
        tree.root.add("after node", after="node")


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


def test_tree_node_add_relative_to_unknown_node_raises_exception():
    tree = Tree[None]("root")
    removed_node = tree.root.add("removed node")
    removed_node.remove()
    with pytest.raises(AddNodeError):
        tree.root.add("node", before=removed_node)
    with pytest.raises(AddNodeError):
        tree.root.add("node", after=removed_node)


def test_tree_node_add_before_node():
    tree = Tree[None]("root")
    node = tree.root.add("node")
    before_node = tree.root.add("before node", before=node)
    tree.root.add("first", before=before_node)
    tree.root.add("after first", before=before_node)
    last = tree.root.add("last", before=4)
    before_last = tree.root.add("before last", before=last)
    tree.root.add("after node", before=before_last)

    assert str(tree.root.children[0].label) == "first"
    assert str(tree.root.children[1].label) == "after first"
    assert str(tree.root.children[2].label) == "before node"
    assert str(tree.root.children[3].label) == "node"
    assert str(tree.root.children[4].label) == "after node"
    assert str(tree.root.children[5].label) == "before last"
    assert str(tree.root.children[6].label) == "last"


def test_tree_node_add_after_node():
    tree = Tree[None]("root")
    node = tree.root.add("node")
    after_node = tree.root.add("after node", after=node)
    first = tree.root.add("first", after=-3)
    after_first = tree.root.add("after first", after=first)
    tree.root.add("before node", after=after_first)
    before_last = tree.root.add("before last", after=after_node)
    tree.root.add("last", after=before_last)

    assert str(tree.root.children[0].label) == "first"
    assert str(tree.root.children[1].label) == "after first"
    assert str(tree.root.children[2].label) == "before node"
    assert str(tree.root.children[3].label) == "node"
    assert str(tree.root.children[4].label) == "after node"
    assert str(tree.root.children[5].label) == "before last"
    assert str(tree.root.children[6].label) == "last"


def test_tree_node_add_leaf_before_or_after():
    tree = Tree[None]("root")
    leaf = tree.root.add_leaf("leaf")
    tree.root.add_leaf("before leaf", before=leaf)
    tree.root.add_leaf("after leaf", after=leaf)
    tree.root.add_leaf("first", before=0)
    tree.root.add_leaf("last", after=-1)

    assert str(tree.root.children[0].label) == "first"
    assert str(tree.root.children[1].label) == "before leaf"
    assert str(tree.root.children[2].label) == "leaf"
    assert str(tree.root.children[3].label) == "after leaf"
    assert str(tree.root.children[4].label) == "last"
