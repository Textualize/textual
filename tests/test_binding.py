import pytest

from textual.binding import Bindings, Binding

BINDING1 = Binding("a,b", action="action1", description="description1")
BINDING2 = Binding("c", action="action2", description="description2")


@pytest.fixture
def bindings():
    yield Bindings([BINDING1, BINDING2])


def test_bindings_get_key(bindings):
    assert bindings.get_key("b") == Binding("b", action="action1", description="description1")
    assert bindings.get_key("c") == BINDING2


def test_bindings_merge_simple(bindings):
    left = Bindings([BINDING1])
    right = Bindings([BINDING2])
    assert Bindings.merge([left, right]).keys == bindings.keys


def test_bindings_merge_overlap():
    left = Bindings([BINDING1])
    another_binding = Binding("a", action="another_action", description="another_description")
    assert Bindings.merge([left, Bindings([another_binding])]).keys == {
        "a": another_binding,
        "b": Binding("b", action="action1", description="description1"),
    }
