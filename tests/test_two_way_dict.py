import pytest

from textual._two_way_dict import TwoWayDict


@pytest.fixture
def two_way_dict():
    return TwoWayDict(
        {
            1: 10,
            2: 20,
            3: 30,
        }
    )


def test_get(two_way_dict):
    assert two_way_dict.get(1) == 10


def test_get_key(two_way_dict):
    assert two_way_dict.get_key(30) == 3


def test_set_item(two_way_dict):
    two_way_dict[40] = 400
    assert two_way_dict.get(40) == 400
    assert two_way_dict.get_key(400) == 40


def test_len(two_way_dict):
    assert len(two_way_dict) == 3


def test_delitem(two_way_dict):
    assert two_way_dict.get(3) == 30
    assert two_way_dict.get_key(30) == 3
    del two_way_dict[3]
    assert two_way_dict.get(3) is None
    assert two_way_dict.get_key(30) is None


def test_contains(two_way_dict):
    assert 1 in two_way_dict
    assert 10 not in two_way_dict
