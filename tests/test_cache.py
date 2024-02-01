from __future__ import annotations, unicode_literals

import pytest

from textual.cache import FIFOCache, LRUCache


def test_lru_cache():
    cache = LRUCache(3)

    assert str(cache) == "<LRUCache size=0 maxsize=3 hits=0 misses=0>"

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


def test_lru_cache_hits():
    cache = LRUCache(4)
    assert cache.hits == 0
    assert cache.misses == 0

    try:
        cache["foo"]
    except KeyError:
        assert cache.hits == 0
        assert cache.misses == 1

    cache["foo"] = 1
    assert cache.hits == 0
    assert cache.misses == 1

    cache["foo"]
    cache["foo"]

    assert cache.hits == 2
    assert cache.misses == 1

    cache.get("bar")
    assert cache.hits == 2
    assert cache.misses == 2

    cache.get("foo")
    assert cache.hits == 3
    assert cache.misses == 2

    assert str(cache) == "<LRUCache size=1 maxsize=4 hits=3 misses=2>"


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


def test_lru_cache_maxsize():
    cache = LRUCache(3)

    # Be sure that maxsize reports what we gave above.
    assert cache.maxsize == 3, "Incorrect cache maxsize"

    # Now resize the cache by setting maxsize.
    cache.maxsize = 30

    # Check that it's reporting that back.
    assert cache.maxsize == 30, "Incorrect cache maxsize after setting it"

    # Add more than maxsize items to the cache and be sure
    for spam in range(cache.maxsize + 10):
        cache[f"spam{spam}"] = spam

    # Finally, check the cache is the max size we set.
    assert len(cache) == 30, "Cache grew too large given maxsize"


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


def test_fifo_cache():
    cache = FIFOCache(4)
    assert len(cache) == 0
    assert not cache
    assert "foo" not in cache
    cache["foo"] = 1
    assert "foo" in cache
    assert len(cache) == 1
    assert cache
    cache["bar"] = 2
    cache["baz"] = 3
    cache["egg"] = 4
    # Cache is full
    assert list(cache.keys()) == ["foo", "bar", "baz", "egg"]
    assert len(cache) == 4
    cache["Paul"] = 100
    assert list(cache.keys()) == ["bar", "baz", "egg", "Paul"]
    assert len(cache) == 4
    assert cache["baz"] == 3
    assert cache["bar"] == 2
    cache["Chani"] = 101
    assert list(cache.keys()) == ["baz", "egg", "Paul", "Chani"]
    assert len(cache) == 4
    cache.clear()
    assert len(cache) == 0
    assert list(cache.keys()) == []


def test_fifo_cache_hits():
    cache = FIFOCache(4)
    assert cache.hits == 0
    assert cache.misses == 0

    try:
        cache["foo"]
    except KeyError:
        assert cache.hits == 0
        assert cache.misses == 1

    cache["foo"] = 1
    assert cache.hits == 0
    assert cache.misses == 1

    cache["foo"]
    cache["foo"]

    assert cache.hits == 2
    assert cache.misses == 1

    cache.get("bar")
    assert cache.hits == 2
    assert cache.misses == 2

    cache.get("foo")
    assert cache.hits == 3
    assert cache.misses == 2

    assert str(cache) == "<FIFOCache maxsize=4 hits=3 misses=2>"


def test_discard():
    cache = LRUCache(maxsize=3)
    cache.set("key1", "value1")
    cache.set("key2", "value2")
    cache.set("key3", "value3")

    assert len(cache) == 3
    assert cache.get("key1") == "value1"

    cache.discard("key1")

    assert len(cache) == 2
    assert cache.get("key1") is None

    cache.discard("key4")  # key that does not exist

    assert len(cache) == 2  # size should not change


def test_discard_regression():
    """Regression test for https://github.com/Textualize/textual/issues/3537"""

    cache = LRUCache(maxsize=3)
    cache[1] = "foo"
    cache[2] = "bar"
    cache[3] = "baz"
    cache[4] = "egg"

    assert cache.keys() == {2, 3, 4}

    cache.discard(2)
    assert cache.keys() == {3, 4}

    cache[5] = "bob"
    assert cache.keys() == {3, 4, 5}

    cache.discard(5)
    assert cache.keys() == {3, 4}

    cache.discard(4)
    cache.discard(3)

    assert cache.keys() == set()
