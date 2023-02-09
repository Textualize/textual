from string import ascii_lowercase

import pytest

from textual.app import App
from textual.binding import Binding, BindingError, Bindings, InvalidBinding, NoBinding

BINDING1 = Binding("a,b", action="action1", description="description1")
BINDING2 = Binding("c", action="action2", description="description2")
BINDING3 = Binding(" d   , e ", action="action3", description="description3")


@pytest.fixture
def bindings():
    yield Bindings([BINDING1, BINDING2])


@pytest.fixture
def more_bindings():
    yield Bindings([BINDING1, BINDING2, BINDING3])


def test_bindings_get_key(bindings):
    assert bindings.get_key("b") == Binding(
        "b", action="action1", description="description1"
    )
    assert bindings.get_key("c") == BINDING2
    with pytest.raises(NoBinding):
        bindings.get_key("control+meta+alt+shift+super+hyper+t")


def test_bindings_get_key_spaced_list(more_bindings):
    assert more_bindings.get_key("d").action == more_bindings.get_key("e").action


def test_bindings_merge_simple(bindings):
    left = Bindings([BINDING1])
    right = Bindings([BINDING2])
    assert Bindings.merge([left, right]).keys == bindings.keys


def test_bindings_merge_overlap():
    left = Bindings([BINDING1])
    another_binding = Binding(
        "a", action="another_action", description="another_description"
    )
    assert Bindings.merge([left, Bindings([another_binding])]).keys == {
        "a": another_binding,
        "b": Binding("b", action="action1", description="description1"),
    }


def test_bad_binding_tuple():
    with pytest.raises(BindingError):
        _ = Bindings((("a", "action"),))
    with pytest.raises(BindingError):
        _ = Bindings((("a", "action", "description", "too much"),))


def test_binding_from_tuples():
    assert (
        Bindings(((BINDING2.key, BINDING2.action, BINDING2.description),)).get_key("c")
        == BINDING2
    )


def test_shown():
    bindings = Bindings(
        [
            Binding(
                key,
                action=f"action_{key}",
                description=f"Emits {key}",
                show=bool(ord(key) % 2),
            )
            for key in ascii_lowercase
        ]
    )
    assert len(bindings.shown_keys) == (len(ascii_lowercase) / 2)


def test_invalid_binding():
    with pytest.raises(InvalidBinding):

        class BrokenApp(App):
            BINDINGS = [(",,,", "foo", "Broken")]

    with pytest.raises(InvalidBinding):

        class BrokenApp(App):
            BINDINGS = [(", ,", "foo", "Broken")]
