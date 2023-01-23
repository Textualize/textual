import pytest

from textual._two_way_dict import TwoWayDict


@pytest.fixture
def map():
    return TwoWayDict(
        {
            1: 10,
            2: 20,
            3: 30,
        }
    )


def test_get(map):
    assert map.get(1) == 10


def test_get_default_none(map):
    assert map.get(9999) is None


def test_get_default_supplied(map):
    assert map.get(9999, -123) == -123


def test_get_key(map):
    assert map.get_key(30) == 3


def test_get_key_default_none(map):
    assert map.get_key(9999) is None


def test_get_key_default_supplied(map):
    assert map.get_key(9999, -123) == -123


def test_set_item(map):
    map[40] = 400
    assert map.get(40) == 400
    assert map.get_key(400) == 40


def test_len(map):
    assert len(map) == 3


def test_delitem(map):
    assert map.get(3) == 30
    assert map.get_key(30) == 3
    del map[3]
    assert map.get(3) is None
    assert map.get_key(30) is None
