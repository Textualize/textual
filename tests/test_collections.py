import pytest

from typing import Iterable
from textual._collections import ImmutableSequence

def wrap(source: Iterable[int]) -> ImmutableSequence[int]:
    """Wrap an itertable of integers inside an immutable sequence."""
    return ImmutableSequence[int](source)


def test_empty_immutable_sequence() -> None:
    """An empty immutable sequence should act as anticipated."""
    assert len(wrap([])) == 0
    assert bool(wrap([])) is False
    assert list(wrap([])) == []


def test_non_empty_immutable_sequence() -> None:
    """A non-empty immutable sequence should act as anticipated."""
    assert len(wrap([0])) == 1
    assert bool(wrap([0])) is True
    assert list(wrap([0])) == [0]


def test_immutable_sequence_from_empty_iter() -> None:
    """An immutable sequence around an empty iterator should act as anticipated."""
    assert len(wrap([])) == 0
    assert bool(wrap([])) is False
    assert list(wrap(iter([]))) == []


def test_immutable_sequence_from_non_empty_iter() -> None:
    """An immutable sequence around a non-empty iterator should act as anticipated."""
    assert len(wrap(range(23))) == 23
    assert bool(wrap(range(23))) is True
    assert list(wrap(range(23))) == list(range(23))


def test_no_assign_to_immutable_sequence() -> None:
    """It should not be possible to assign into an immutable sequence."""
    tester = wrap([1,2,3,4,5])
    with pytest.raises(TypeError):
        tester[0] = 23
    with pytest.raises(TypeError):
        tester[0:3] = 23


def test_no_del_from_iummutable_sequence() -> None:
    """It should not be possible delete an item from an immutable sequence."""
    tester = wrap([1,2,3,4,5])
    with pytest.raises(TypeError):
        del tester[0]


def test_get_item_from_immutable_sequence() -> None:
    """It should be possible to get an item from an immutable sequence."""
    assert wrap(range(10))[0] == 0
    assert wrap(range(10))[-1] == 9

def test_get_slice_from_immutable_sequence() -> None:
    """It should be possible to get a slice from an immutable sequence."""
    assert list(wrap(range(10))[0:2]) == [0,1]
    assert list(wrap(range(10))[0:-1]) == [0,1,2,3,4,5,6,7,8]


def test_immutable_sequence_contains() -> None:
    """It should be possible to see if an immutable sequence contains a value."""
    tester = wrap([1,2,3,4,5])
    assert 1 in tester
    assert 11 not in tester


def test_immutable_sequence_index() -> None:
    tester = wrap([1,2,3,4,5])
    assert tester.index(1) == 0
    with pytest.raises(ValueError):
        _ = tester.index(11)


def test_reverse_immutable_sequence() -> None:
    assert list(reversed(wrap([1,2]))) == [2,1]
