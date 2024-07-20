import pytest

from textual._node_list import NodeList
from textual.widget import Widget


def test_empty_list():
    """Does an empty node list report as being empty?"""
    assert len(NodeList()) == 0


def test_add_one():
    """Does adding a node to the node list report as having one item?"""
    nodes = NodeList()
    nodes._append(Widget())
    assert len(nodes) == 1


def test_length_hint():
    """Check length hint dunder method."""
    nodes = NodeList()
    assert nodes.__length_hint__() == 0
    nodes._append(Widget())
    nodes._append(Widget())
    nodes._append(Widget())
    assert nodes.__length_hint__() == 3


def test_repeat_add_one():
    """Does adding the same item to the node list ignore the additional adds?"""
    nodes = NodeList()
    widget = Widget()
    for _ in range(1000):
        nodes._append(widget)
    assert len(nodes) == 1


def test_insert():
    nodes = NodeList()
    widget1 = Widget()
    widget2 = Widget()
    widget3 = Widget()
    nodes._append(widget1)
    nodes._append(widget3)
    nodes._insert(1, widget2)
    assert list(nodes) == [widget1, widget2, widget3]


def test_truthy():
    """Does a node list act as a truthy object?"""
    nodes = NodeList()
    assert not bool(nodes)
    nodes._append(Widget())
    assert bool(nodes)


def test_contains():
    """Can we check if a widget is (not) within the list?"""
    widget = Widget()
    nodes = NodeList()
    assert widget not in nodes
    nodes._append(widget)
    assert widget in nodes
    assert Widget() not in nodes


def test_index():
    """Can we get the index of a widget in the list?"""
    widget = Widget()
    nodes = NodeList()
    with pytest.raises(ValueError):
        _ = nodes.index(widget)
    nodes._append(widget)
    assert nodes.index(widget) == 0


def test_remove():
    """Can we remove a widget we've added?"""
    widget = Widget()
    nodes = NodeList()
    nodes._append(widget)
    assert widget in nodes
    nodes._remove(widget)
    assert widget not in nodes


def test_clear():
    """Can we clear the list?"""
    nodes = NodeList()
    assert len(nodes) == 0
    widgets = [Widget() for _ in range(1000)]
    for widget in widgets:
        nodes._append(widget)
    assert len(nodes) == 1000
    for widget in widgets:
        assert widget in nodes
    nodes._clear()
    assert len(nodes) == 0
    for widget in widgets:
        assert widget not in nodes


def test_listy():
    nodes = NodeList()
    widget1 = Widget()
    widget2 = Widget()
    nodes._append(widget1)
    nodes._append(widget2)
    assert list(nodes) == [widget1, widget2]
    assert list(reversed(nodes)) == [widget2, widget1]
    assert nodes[0] == widget1
    assert nodes[1] == widget2
    assert nodes[0:2] == [widget1, widget2]
