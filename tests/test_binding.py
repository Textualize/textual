from string import ascii_lowercase

import pytest

from textual.app import App
from textual.binding import (
    Binding,
    BindingError,
    BindingsMap,
    InvalidBinding,
    NoBinding,
)

BINDING1 = Binding("a,b", action="action1", description="description1")
BINDING2 = Binding("c", action="action2", description="description2")
BINDING3 = Binding(" d   , e ", action="action3", description="description3")


@pytest.fixture
def bindings():
    yield BindingsMap([BINDING1, BINDING2])


@pytest.fixture
def more_bindings():
    yield BindingsMap([BINDING1, BINDING2, BINDING3])


def test_bindings_get_key(bindings):
    assert bindings.get_bindings_for_key("b") == [
        Binding("b", action="action1", description="description1")
    ]
    assert bindings.get_bindings_for_key("c") == [BINDING2]
    with pytest.raises(NoBinding):
        bindings.get_bindings_for_key("control+meta+alt+shift+super+hyper+t")


def test_bindings_get_key_spaced_list(more_bindings):
    assert (
        more_bindings.get_bindings_for_key("d")[0].action
        == more_bindings.get_bindings_for_key("e")[0].action
    )


def test_bindings_merge_simple(bindings):
    left = BindingsMap([BINDING1])
    right = BindingsMap([BINDING2])
    assert BindingsMap.merge([left, right]).key_to_bindings == bindings.key_to_bindings


def test_bindings_merge_overlap():
    left = BindingsMap([BINDING1])
    another_binding = Binding(
        "a", action="another_action", description="another_description"
    )
    assert BindingsMap.merge(
        [left, BindingsMap([another_binding])]
    ).key_to_bindings == {
        "a": [
            Binding("a", action="action1", description="description1"),
            another_binding,
        ],
        "b": [Binding("b", action="action1", description="description1")],
    }


def test_bad_binding_tuple():
    with pytest.raises(BindingError):
        _ = BindingsMap((("a",),))
    with pytest.raises(BindingError):
        _ = BindingsMap((("a", "action", "description", "too much"),))


def test_binding_from_tuples():
    assert BindingsMap(
        ((BINDING2.key, BINDING2.action, BINDING2.description),)
    ).get_bindings_for_key("c") == [BINDING2]


def test_shown():
    bindings = BindingsMap(
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
