from __future__ import annotations
from __future__ import unicode_literals

import pytest

from textual._cache import LRUCache


def test_lru_cache():
    cache = LRUCache(3)

    # insert some values
    cache["foo"] = 1
    cache["bar"] = 2
    cache["baz"] = 3
    assert "foo" in cache
    assert "bar" in cache
    assert "baz" in cache

    #  Cache size is 3, so the following should kick oldest one out
    cache["egg"] = 4
    assert "foo" not in cache
    assert "egg" in cache

    # cache is now full
    # look up two keys
    cache["bar"]
    cache["baz"]

    # Insert a new value
    cache["eggegg"] = 5
    assert len(cache) == 3
    # Check it kicked out the 'oldest' key
    assert "egg" not in cache
    assert "eggegg" in cache


def test_lru_cache_get():
    cache = LRUCache(3)

    # insert some values
    cache["foo"] = 1
    cache["bar"] = 2
    cache["baz"] = 3
    assert "foo" in cache

    #  Cache size is 3, so the following should kick oldest one out
    cache["egg"] = 4
    # assert len(cache) == 3
    assert cache.get("foo") is None
    assert "egg" in cache

    # cache is now full
    # look up two keys
    cache.get("bar")
    cache.get("baz")

    # Insert a new value
    cache["eggegg"] = 5
    # Check it kicked out the 'oldest' key
    assert "egg" not in cache
    assert "eggegg" in cache


def test_lru_cache_mapping():
    """Test cache values can be set and read back."""
    cache = LRUCache(3)
    cache["foo"] = 1
    cache.set("bar", 2)
    cache.set("baz", 3)
    assert cache["foo"] == 1
    assert cache["bar"] == 2
    assert cache.get("baz") == 3


def test_lru_cache_clear():
    cache = LRUCache(3)
    assert len(cache) == 0
    cache["foo"] = 1
    assert "foo" in cache
    assert len(cache) == 1
    cache.clear()
    assert "foo" not in cache
    assert len(cache) == 0


def test_lru_cache_bool():
    cache = LRUCache(3)
    assert not cache
    cache["foo"] = "bar"
    assert cache


@pytest.mark.parametrize(
    "keys,expected",
    [
        ((), ()),
        (("foo",), ("foo",)),
        (("foo", "bar"), ("foo", "bar")),
        (("foo", "bar", "baz"), ("foo", "bar", "baz")),
        (("foo", "bar", "baz", "egg"), ("bar", "baz", "egg")),
        (("foo", "bar", "baz", "egg", "bob"), ("baz", "egg", "bob")),
    ],
)
def test_lru_cache_evicts(keys: list[str], expected: list[str]):
    """Test adding adding additional values evicts oldest key"""
    cache = LRUCache(3)
    for value, key in enumerate(keys):
        cache[key] = value
    assert tuple(cache.keys()) == expected


@pytest.mark.parametrize(
    "keys,expected_len",
    [
        ((), 0),
        (("foo",), 1),
        (("foo", "bar"), 2),
        (("foo", "bar", "baz"), 3),
        (("foo", "bar", "baz", "egg"), 3),
        (("foo", "bar", "baz", "egg", "bob"), 3),
    ],
)
def test_lru_cache_len(keys: list[str], expected_len: int):
    """Test adding adding additional values evicts oldest key"""
    cache = LRUCache(3)
    for value, key in enumerate(keys):
        cache[key] = value
    assert len(cache) == expected_len
