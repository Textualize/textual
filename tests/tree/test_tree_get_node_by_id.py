from typing import cast

import pytest

from textual.widgets import Tree
from textual.widgets.tree import NodeID, UnknownNodeID


def test_get_tree_node_by_id() -> None:
    """It should be possible to get a TreeNode by its ID."""
    tree = Tree[None]("Anakin")
    child = tree.root.add("Leia")
    grandchild = child.add("Ben")
    assert tree.get_node_by_id(tree.root.id).id == tree.root.id
    assert tree.get_node_by_id(child.id).id == child.id
    assert tree.get_node_by_id(grandchild.id).id == grandchild.id
    with pytest.raises(UnknownNodeID):
        tree.get_node_by_id(cast(NodeID, grandchild.id + 1000))
